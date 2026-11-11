import pytest
from unittest.mock import Mock
from src.service import UserService, User, UserRepository

# Тест 1: Успешная регистрация
def test_register_success():
    # Создаем мок репозитория. 
    # spec=UserRepository я добавил, чтобы мок знал только настоящие методы класса
    repo = Mock(spec=UserRepository)
    
    # Говорим моку: если будут искать email, верни None (значит такого юзера нет)
    repo.find_by_email.return_value = None
    
    # Создаем сервис и передаем туда мок
    service = UserService(repo)
    
    # Вызываем метод
    new_user = service.register("test@mail.ru", "Иван")
    
    # Проверяем, что вернулся объект User с правильными данными
    assert isinstance(new_user, User)
    assert new_user.email == "test@mail.ru"
    assert new_user.name == "Иван"
    
    # Проверяем, что репозиторий искал именно этот email
    repo.find_by_email.assert_called_once_with("test@mail.ru")
    
    # Проверяем, что метод save вызвался ровно 1 раз
    repo.save.assert_called_once()
    
    # Достаем того пользователя, которого передали в save, и проверяем его
    saved_user = repo.save.call_args[0][0]  # первый аргумент первого вызова
    assert saved_user.email == "test@mail.ru"


# Тест 2: Ошибка, если email уже занят
def test_register_email_already_exists():
    repo = Mock(spec=UserRepository)
    
    # Тут наоборот: говорим моку, что юзер с таким email УЖЕ есть
    # Создаем фейкового пользователя и возвращаем его
    fake_user = User("old@mail.ru", "Старый")
    repo.find_by_email.return_value = fake_user
    
    service = UserService(repo)
    
    # Проверяем, что вылетит ValueError с нужным текстом
    with pytest.raises(ValueError, match="Email already registered"):
        service.register("old@mail.ru", "Новый")
    
    # Самое главное: метод save НЕ должен вызываться, ведь юзер уже есть!
    repo.save.assert_not_called()


# Тест 3: Получение существующего пользователя
def test_get_user_success():
    repo = Mock(spec=UserRepository)
    
    # Настраиваем, что юзер найден
    expected_user = User("find@mail.ru", "Найденный")
    repo.find_by_email.return_value = expected_user
    
    service = UserService(repo)
    result = service.get_user("find@mail.ru")
    
    # Проверяем, что вернулся именно тот юзер, которого мы заложили в мок
    assert result == expected_user


# Тест 4: Ошибка, если пользователя нет
def test_get_user_not_found():
    repo = Mock(spec=UserRepository)
    
    # Говорим, что поиск ничего не нашел
    repo.find_by_email.return_value = None
    
    service = UserService(repo)
    
    # Ждем ошибку LookupError
    with pytest.raises(LookupError, match="User not found"):
        service.get_user("no@mail.ru")

# Тест 5: Ошибка, падение БД
def test_register_database_exception():
    repo = Mock(spec=UserRepository)
    # Имитируем таймаут или падение БД
    repo.find_by_email.side_effect = Exception("DB connection timeout")
    
    service = UserService(repo)
    
    with pytest.raises(Exception, match="DB connection timeout"):
        service.register("test@mail.ru", "Иван")