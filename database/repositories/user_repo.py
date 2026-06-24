from core.base_repo import BaseRepo
from database.models import User
from api.return_schemas.expense.categories.request import ExpenseCategoryRequest


class UserRepo(BaseRepo):
    @property
    def model(self):
        return User


    # def create_expense_category(self):
