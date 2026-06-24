from sqlalchemy.orm import Session

from api.return_schemas import ExpenseCategoryRequest
from database.models import ExpenseCategory
from database.repositories.expense_repo.expense_category import ExpenseCategoryRepo
from exceptions import ExpenseCategoryNameAlreadyExists


class ExpenseCategoryService:
    def __init__(self,db: Session):
        self.repo = ExpenseCategoryRepo(db)

    def create_unique_expense_category(self, request: ExpenseCategoryRequest) -> ExpenseCategory:
        if self.repo.get_by_name(request.name) is None:
            return self.repo.create_expense_category(request)

        raise ExpenseCategoryNameAlreadyExists(request.name)


