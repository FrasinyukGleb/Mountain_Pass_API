from starlette import status
from starlette.exceptions import HTTPException


class PassNotFoundError(HTTPException):
    def __init__(self, mountain_pass_id: int):
        super(PassNotFoundError, self).__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Не удалось найти запись с id {mountain_pass_id}',
        )


class PassUpdateError(HTTPException):
    def __init__(self, ex):
        super(PassUpdateError, self).__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ex),
        )


class UserNotFoundByEmailError(HTTPException):
    def __init__(self, user_email: str):
        super(UserNotFoundByEmailError, self).__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Пользователь {user_email} не найден!',
        )


class IncorrectPassStatus(HTTPException):
    def __init__(self, mountain_pass_status: str):
        super(IncorrectPassStatus, self).__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'Ошибка обновления. Запись в статусе - {mountain_pass_status}',
        )