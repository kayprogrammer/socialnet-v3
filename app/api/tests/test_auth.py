from app.api.utils.auth import Authentication
from app.common.handlers import ErrorCode
from app.models.accounts.tables import Otp

BASE_URL_PATH = "/api/v3/auth"

async def test_register_user(client):
    # Setup
    email = "testregisteruser@example.com"
    password = "testregisteruserpassword"
    user_in = {
        "first_name": "Testregister",
        "last_name": "User",
        "email": email,
        "password": password,
        "terms_agreement": True,
    }

    # Verify that a new user can be registered successfully
    response = await client.post(f"{BASE_URL_PATH}/register", json=user_in)
    assert response.status_code == 201
    assert response.json() == {
        "status": "success",
        "message": "Registration successful",
        "data": {"email": user_in["email"]},
    }

    # Verify that a user with the same email cannot be registered again
    response = await client.post(f"{BASE_URL_PATH}/register", json=user_in)
    assert response.status_code == 422
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.INVALID_ENTRY,
        "message": "Invalid Entry",
        "data": {"email": "Email already registered!"},
    }


async def test_verify_email(mocker, client, test_user):
    otp = "111111"

    # Verify that the email verification fails with an invalid otp
    response = await client.post(
        f"{BASE_URL_PATH}/verify-email", json={"email": test_user.email, "otp": otp}
    )
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.INCORRECT_OTP,
        "message": "Incorrect Otp",
    }
    # Verify that the email verification succeeds with a valid otp
    otp = await Otp.objects().create(user=test_user.id)
    
    response = await client.post(
        f"{BASE_URL_PATH}/verify-email",
        json={"email": test_user.email, "otp": otp.code},
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Account verification successful",
    }


async def test_resend_verification_email(mocker, client, test_user):
    user_in = {"email": test_user.email}

    # Verify that an unverified user can get a new email
    
    # Then, attempt to resend the verification email
    response = await client.post(
        f"{BASE_URL_PATH}/resend-verification-email", json=user_in
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Verification email sent",
    }

    # Verify that a verified user cannot get a new email
    test_user.is_email_verified = True
    await test_user.save()
    
    response = await client.post(
        f"{BASE_URL_PATH}/resend-verification-email",
        json={"email": test_user.email},
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Email already verified",
    }

    # Verify that an error is raised when attempting to resend the verification email for a user that doesn't exist
    
    response = await client.post(
        f"{BASE_URL_PATH}/resend-verification-email",
        json={"email": "invalid@example.com"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.INCORRECT_EMAIL,
        "message": "Incorrect Email",
    }


async def test_login(mocker, client, test_user):
    # Test for invalid credentials
    response = await client.post(
        f"{BASE_URL_PATH}/login",
        json={"email": "invalid@email.com", "password": "invalidpassword"},
    )
    assert response.status_code == 401
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.INVALID_CREDENTIALS,
        "message": "Invalid credentials",
    }

    # Test for unverified credentials (email)
    response = await client.post(
        f"{BASE_URL_PATH}/login",
        json={"email": test_user.email, "password": "testpassword"},
    )
    assert response.status_code == 401
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.UNVERIFIED_USER,
        "message": "Verify your email first",
    }

    # Test for valid credentials and verified email address
    test_user.is_email_verified = True
    await test_user.save()
    response = await client.post(
        f"{BASE_URL_PATH}/login",
        json={"email": test_user.email, "password": "testpassword"},
    )
    assert response.status_code == 201
    assert response.json() == {
        "status": "success",
        "message": "Login successful",
        "data": {"access": mocker.ANY, "refresh": mocker.ANY},
    }


async def test_refresh_token(mocker, client, verified_user):
    # Test for invalid refresh token (invalid or expired)
    response = await client.post(
        f"{BASE_URL_PATH}/refresh", json={"refresh": "invalid_refresh_token"}
    )
    assert response.status_code == 401
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.INVALID_TOKEN,
        "message": "Refresh token is invalid or expired",
    }

    # Test for valid refresh token
    refresh = await Authentication.create_refresh_token()
    verified_user.refresh_token = refresh
    await verified_user.save()
    mocker.patch("app.api.utils.auth.Authentication.decode_jwt", return_value=True)
    response = await client.post(
        f"{BASE_URL_PATH}/refresh", json={"refresh": verified_user.refresh_token}
    )
    assert response.status_code == 201
    assert response.json() == {
        "status": "success",
        "message": "Tokens refresh successful",
        "data": {"access": mocker.ANY, "refresh": mocker.ANY},
    }


async def test_get_password_otp(mocker, client, verified_user):
    email = verified_user.email

    password = "testverifieduser123"
    user_in = {"email": email, "password": password}

    
    # Then, attempt to get password reset token
    response = await client.post(
        f"{BASE_URL_PATH}/send-password-reset-otp", json=user_in
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Password otp sent",
    }

    # Verify that an error is raised when attempting to get password reset token for a user that doesn't exist
    
    response = await client.post(
        f"{BASE_URL_PATH}/send-password-reset-otp",
        json={"email": "invalid@example.com"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.INCORRECT_EMAIL,
        "message": "Incorrect Email",
    }


async def test_reset_password(mocker, client, verified_user):
    password_reset_data = {
        "email": verified_user.email,
        "password": "newverifieduserpass",
    }
    otp = "111111"

    # Verify that the password reset verification fails with an incorrect email
    response = await client.post(
        f"{BASE_URL_PATH}/set-new-password",
        json={
            "email": "invalidemail@example.com",
            "otp": otp,
            "password": "newpassword",
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.INCORRECT_EMAIL,
        "message": "Incorrect Email",
    }

    # Verify that the password reset verification fails with an invalid otp
    password_reset_data["otp"] = otp
    response = await client.post(
        f"{BASE_URL_PATH}/set-new-password",
        json=password_reset_data,
    )
    assert response.status_code == 404
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.INCORRECT_OTP,
        "message": "Incorrect Otp",
    }

    # Verify that password reset succeeds
    otp = (await Otp.objects().create(user=verified_user.id)).code
    password_reset_data["otp"] = otp
    
    response = await client.post(
        f"{BASE_URL_PATH}/set-new-password",
        json=password_reset_data,
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Password reset successful",
    }


async def test_logout(authorized_client):
    # Ensures if authorized user logs out successfully
    response = await authorized_client.get(f"{BASE_URL_PATH}/logout")

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Logout successful",
    }

    # Ensures if unauthorized user cannot log out
    response = await authorized_client.get(
        f"{BASE_URL_PATH}/logout", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json() == {
        "status": "failure",
        "code": ErrorCode.INVALID_TOKEN,
        "message": "Auth Token is Invalid or Expired!",
    }
