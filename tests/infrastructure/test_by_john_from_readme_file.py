from infrastructure.ts_unit_of_work import UnitOfWork


def test():

    with UnitOfWork() as do:
        user = do.new_user("Name", "Domain")

    with UnitOfWork() as do:
        modified_user = do.change_name(user.id, "New Name")

    assert user.name == 'Name'
    assert modified_user.name == 'New Name'