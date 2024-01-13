def update_count(model, targeted_obj_id, field="reactions_count", action="add"):
    value = getattr(model, field) + 1 if action == "add" else getattr(model, field) - 1
    model.update({getattr(model, field): value}).where(
        model.id == targeted_obj_id
    ).run_sync()
