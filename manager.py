import shutil
import os
import json
from pathlib import Path

import size_check

class FileManager:

    # mkdir
    @staticmethod
    def make_dir(path):
        if path.exists():
            print('директория или файл уже существует')
        else:
            path.mkdir(parents=True)

    # makefile
    @staticmethod
    def make_file(path):
        if path.exists():
            print('директория или файл не существует')
        else:
            path.touch()

    # cd
    @staticmethod
    def cd(path):
        if path.is_dir():
            os.chdir(path)
        else:
            print('директория не существует')

    # show
    @staticmethod
    def show_file(path):
        if path.is_file():
            print(path.read_text())
        else:
            print('файл не существует')

    # del
    @staticmethod
    def delete(path):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.is_file():
            path.unlink()
        else:
            print('директория или файл не существует')


    def __init__(self, root, username='', size=None):
        self._root = Path(root).resolve()
        if not self._root.is_dir():
            self.make_dir(self._root)
        os.chdir(self._root)
        self._username = username
        self._size = size

    @property
    def working_dir(self):
        return Path.cwd().relative_to(self._root) #os.getcwd

    @property
    def invite(self):
        working_dir = str(
            self.working_dir).replace('\\', '/').replace('.', '/')
        if working_dir[0] != '/':
            working_dir = '/' + working_dir
        if self._username:
            return f'{self._username}:{working_dir}$ '
        else:
            f'{working_dir}$ '

    def write_file(self, path):
        if path.is_file():
            text = input()
            with open(path, 'a') as file:
                file.write(text)
        else:
            print('файл не существует')

    def help_outp(self):
        print("""
Введите:
help - для вывода команд
mkdir "name" - создание папки
mkfile "name" - создание файла 
cd "path or empty"- перемещение между папками
write "name_of_file.txt" "text" -  запись в файл
show "name_of_file.txt" - просмотр текста в файле
del "name_of_file.txt" - удаление файла
exit - выход из программы""")

    def commands_(self):
        while True:
            command, *paths = input(self.invite).split()
            paths = list(map(self._get_path, paths))
            if command == 'mkdir':
                self.make_dir(paths[0])
            elif command == 'mkfile':
                self.make_file(paths[0])
            elif command == 'cd':
                self.cd(paths[0])
            elif command == 'write':
                self.write_file(paths[0])
            elif command == 'show':
                self.show_file(paths[0])
            elif command == 'del':
                self.delete(paths[0])
            elif command == 'help':
                self.help_outp()
            elif command == 'exit':
                break
            else:
                print('команда не найдена')

    def _get_path(self, str_path):
        if str_path[0] == '/':
            path = Path(self._root, str_path[1:])
        elif str_path.find('..') != -1:
            path = Path()
            for path_part in Path(str_path).parts:
                resolved_path_part = Path(path_part).resolve()
                if (path_part == '..' and
                        resolved_path_part.is_relative_to(self._root)):
                    path = resolved_path_part
                elif path_part != '..':
                    path = path.joinpath(path_part)
                else:
                    path = self._root
        else:
            resolved_path = Path(str_path).resolve()
            if (resolved_path.is_absolute() and
                    resolved_path.relative_to(self._root)):
                path = Path(str_path).resolve()
            else:
                path = Path.cwd().joinpath(Path(str_path))
        return path

class multiple_user:

    def __init__(self, users, root=None, size=None):
        self._users = users
        if root is not None:
            self._root = Path(root).resolve()
            self.make_root_dir()
        else:
            self._root = root
        self._size = size
        self._authorized = False
        self._username = None

    def settings(self, filename='settings.json'):
        with open(filename) as file:
            self._root = Path(json.load(file)['working_directory']).resolve()
            self.make_root_dir()
        return self

    def make_root_dir(self):
        if not self._root.is_dir():
            self._root.mkdir(parents=True)

    def authentication(self):
        username = input('Логин: ')
        password = input('Пароль: ')
        if self._users.exists(username):
            if password == self._users.get_password(username):
                self._authorized = True
        else:
            self._users.add(username, password)
            self._authorized = True
        self._username = username

    def start(self):
        if self._authorized:
            user_working_dir = Path(self._root, self._username)
            FileManager(
                user_working_dir,
                self._username,
                self._size
            ).commands_()
        else:
            print('Неправильный пароль')

