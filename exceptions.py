from core.base_exception import AppException

class DataDoesNotExist(AppException):
    def __init__(self, param):
        super().__init__(
            message=f"{param} not found",
            error_code="DATA_DOES_NOT_EXISTS",
            status_code=404
        )
        self.param = param

class UnAuthorized(AppException):
    def __init__(self,msg,status_code=401):
        super().__init__(
            message=msg,
            error_code="UNAUTHORIZED",
            status_code=status_code
        )
        self.status_code = status_code
        self.msg = msg

class ExpenseCategoryNameAlreadyExists(AppException):
    def __init__(self, category_name: str):
        super().__init__(
            message=f"Expense Category name '{category_name}' already exists",
            error_code="EXPENSE_CATEGORY_NAME_EXISTS",
            status_code=422
        )
        self.category_name = category_name