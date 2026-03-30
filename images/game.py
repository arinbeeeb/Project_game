import tkinter as tk
import random
from tkinter import scrolledtext  # многострочный редактор текста с возможностью прокрутки
from tkinter import messagebox  # всплывающие окна
import json  # загрузка статистики в файл
import os  # проверка существования файла
import logging

# Настройка логирования
logging.basicConfig(
    filename='game.log',  # указывает куда сохранять логирование
    level=logging.INFO,  # что писать
    format='%(asctime)s - %(levelname)s - %(message)s',  # шаблон строки - времени, уровня и текста
    encoding='utf-8'
)


class BullsAndCowsGame:  # создаём класс игры
    def __init__(self, root):  # создаём главное окно, для установки значений атрибутов
        self.root = root  # ссылка на объект класса, все методы могут работать с этим окном
        self.root.title("БЫКИ И КОРОВЫ")  # заголовок
        self.root.geometry("600x600")  # размеры окна (увеличил для истории)
        self.root.resizable(False, False)  # запрет на изменение размера окна

        self.secret_number = ""  # хранение секретного числа
        self.attempts = 0  # счетчик кол-ва попыток
        self.game_active = True  # активность игры: true-продолжение игры, false-игра окончена
        self.history_file = "game_history.txt"  # имя файла игры
        
        # статистика
        self.stats = {
            'games_played': 0,
            'wins': 0,
            'total_attempts': 0,
            'best_attempts': 0
        }
        self.load_stats()  # загружаем статистику из файла

        self.create_widgets()  # создание интерфейса: поля, кнопки
        self.new_game()  # начало новой игры: генерация числа, сброс кол-ва попыток, очистка поля ввода

        logging.info("игра 'Быки и коровы' запущена")  # запись о начале игры, логирование

    def generate_secret_number(self):  # генерация секретного числа
        digits = list(range(10))  # генерирует число от 0 до 9
        random.shuffle(digits)  # перемешиваем эти числа
        if digits[0] == 0:  # проверка на 0 в начале
            digits[0], digits[1] = digits[1], digits[0]  # меняем местами
        secret = digits[:4]  # берем первые 4 числа из перемешанных
        secret_str = ''.join(map(str, secret))  # список цифр переделываем в строку
        logging.info(f"загадано секретное число: {secret_str}")  # записываем в логирование загаданное число
        return secret_str  # возвращаем число в виде строки

    def create_widgets(self):  # создаём интерфейс
        # заголовок
        title_frame = tk.Frame(self.root, bg='navy', height=60)  # создание рамки для заголовка
        title_frame.pack(fill=tk.X)  # текст по ширине
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text="БЫКИ И КОРОВЫ",  # название
                               font=("Arial", 20, "bold"),  # параметры шрифта
                               bg='navy', fg='white')  # цвета оформления
        title_label.pack(expand=True)

        # основная рамка - добавляемая в окно!
        main_frame = tk.Frame(self.root, padx=20, pady=10)  # создание места для игровых элементов
        main_frame.pack()  

        self.secret_label = tk.Label(main_frame, text="", font=("Arial", 10), fg="gray")  # метка для отображения секретного числа
        self.secret_label.pack()  # хранит объект и размещает виджет в окне

        # рамка для ввода
        input_frame = tk.Frame(main_frame)  # создание поля, рамки
        input_frame.pack(pady=10)  # отступ сверху и снизу по 10

        tk.Label(input_frame, text="ДОГАДКА:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5) #параметры

        self.entry = tk.Entry(input_frame, width=10, font=("Arial", 16), justify='center')  # параметры создания поля
        self.entry.pack(side=tk.LEFT, padx=5)
        self.entry.bind('<Return>', self.make_guess)  # создание Enter для удобства

        self.guess_btn = tk.Button(input_frame, text="ПРОВЕРИТЬ",  # создание кнопки проверки
                                   command=self.make_guess,  # сравнение догадки с секретным числом
                                   font=("Arial", 12, "bold"),
                                   bg='lightblue', width=12)
        self.guess_btn.pack(side=tk.LEFT, padx=5)

        # счетчик попыток, статус игры
        stats_frame = tk.Frame(main_frame, bg='lightgray', relief=tk.GROOVE, bd=2)
        stats_frame.pack(fill=tk.X, pady=10, padx=5)

        self.attempts_label = tk.Label(stats_frame, text="ПОПЫТОК: 0",
                                       font=("Arial", 12), bg='lightgray')
        self.attempts_label.pack(side=tk.LEFT, padx=20, pady=5)

        self.status_label = tk.Label(stats_frame, text="ИГРА АКТИВНА",
                                      font=("Arial", 12), bg='lightgray', fg='green')
        self.status_label.pack(side=tk.RIGHT, padx=20, pady=5)

        # кнопки управления
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)

        self.new_game_btn = tk.Button(button_frame, text="НОВАЯ ИГРА",
                                      command=self.new_game,
                                      font=("Arial", 11), bg='lightgreen', width=12)
        self.new_game_btn.pack(side=tk.LEFT, padx=5)

        self.rules_btn = tk.Button(button_frame, text="ПРАВИЛА",
                                   command=self.show_rules,
                                   font=("Arial", 11), bg='lightyellow', width=12)
        self.rules_btn.pack(side=tk.LEFT, padx=5)

        self.stats_btn = tk.Button(button_frame, text="СТАТИСТИКА",
                                   command=self.show_stats,
                                   font=("Arial", 11), bg='lightblue', width=12)
        self.stats_btn.pack(side=tk.LEFT, padx=5)

        # текстовое поле для истории ходов
        history_label = tk.Label(main_frame, text="ИСТОРИЯ ХОДОВ:", font=("Arial", 10, "bold"))
        history_label.pack(anchor=tk.W, pady=(10, 0))

        self.history_text = scrolledtext.ScrolledText(main_frame, width=60, height=12,
                                                       font=("Courier", 9), state='normal')
        self.history_text.pack(pady=5)

    def make_guess(self):  # обработка ввода числа
        if not self.game_active:
            messagebox.showinfo("и гра окончена", "начните новую игру")
            return

        guess = self.entry.get().strip()
        self.entry.delete(0, tk.END)  # очистка поля ввода

        # проверка корректности ввода
        if len(guess) != 4:
            self.add_to_history(f"ОШИБКА: '{guess}' - введите ровно 4 цифры")
            logging.warning(f"попытка ввода не из 4 цифр: {guess}")
            return

        if not guess.isdigit():  # возвращает правду если все символы, это числа от 0-9
            self.add_to_history(f"ОШИБКА: '{guess}' - можно вводить только цифры")
            logging.warning(f"Попытка ввода нецифровых символов: {guess}")
            return

        if len(set(guess)) != 4:  # если в числе есть повторяющиеся цифры, размер множества будет меньше 4
            self.add_to_history(f"ОШИБКА: '{guess}' - цифры не должны повторяться")
            logging.warning(f"Попытка ввода с повторяющимися цифрами: {guess}")
            return

        # подсчет быков и коров
        bulls = 0
        cows = 0

        for i in range(4):
            if guess[i] == self.secret_number[i]:
                bulls += 1  # цифра есть, на своем месте
            elif guess[i] in self.secret_number:
                cows += 1  # цифра есть, но не на своем месте

        self.attempts += 1  # обновление счетчика попыток
        self.attempts_label.config(text=f"Попыток: {self.attempts}")

        # запись хода
        move_text = f"Попытка #{self.attempts}: {guess} → БЫКИ: {bulls}, КОРОВЫ: {cows}"
        self.add_to_history(move_text)

        logging.info(f"Ход #{self.attempts}: {guess} → Быки: {bulls}, Коровы: {cows}")

        if bulls == 4:  # все цифры угаданы
            self.game_over(win=True)
        else:
            self.entry.focus_set()

    def game_over(self, win):  # конец игры
        self.game_active = False  # запрет на новый ход
        self.guess_btn.config(state='disabled')
        self.entry.config(state='disabled')  # блокирует ввод

        if win:  # блок при победе
            message = f"ПОБЕДА \n\nВЫ УГАДАЛИ ЧИСЛО {self.secret_number}\nЗА {self.attempts} ПОПЫТОК"
            self.status_label.config(text="ПОБЕДА!", fg='green')
            self.add_to_history(f"\n=== ПОБЕДА! ЧИСЛО УГАДАНО ЗА {self.attempts} ПОПЫТОК ===\n")
            
            # обновляем статистику (при победе0
            self.stats['games_played'] += 1
            self.stats['wins'] += 1
            self.stats['total_attempts'] += self.attempts
            if self.stats['best_attempts'] == 0 or self.attempts < self.stats['best_attempts']:
                self.stats['best_attempts'] = self.attempts
            self.save_stats()
        else:  # блок при поражении
            message = f"ПОРАЖЕНИЕ \n\nЗагаданное число: {self.secret_number}"
            self.status_label.config(text="ПОРАЖЕНИЕ", fg='red')
            self.add_to_history(f"\n=== ПОРАЖЕНИЕ! загадано: {self.secret_number} ===\n")
            
            # обновляем статистику (при поражении)
            self.stats['games_played'] += 1
            self.save_stats()

        # окно с результатом
        result_window = tk.Toplevel(self.root)
        result_window.title("Результат игры")
        result_window.geometry("320x250")
        result_window.resizable(False, False)
        result_window.grab_set()

        tk.Label(result_window, text=message, font=("Arial", 12),
                 wraplength=280, pady=20).pack()

        btn_frame = tk.Frame(result_window)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="НОВАЯ ИГРА",
                 command=lambda: (result_window.destroy(), self.new_game()),
                 font=("Arial", 10), bg='lightgreen', width=12).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="ЗАКРЫТЬ",
                 command=result_window.destroy,
                 font=("Arial", 10), width=12).pack(side=tk.LEFT, padx=5)

    def new_game(self):  # начать новую игру
        self.secret_number = self.generate_secret_number()  # генерирует новое случайное число
        self.attempts = 0  # сброс счетчика попыток
        self.game_active = True  # игра снова активна

        self.attempts_label.config(text="Попыток: 0")  # сброс счетчика на экране
        self.status_label.config(text="Игра продолжается", fg='green')  # статус о готовности
        self.guess_btn.config(state='normal')
        self.entry.config(state='normal')
        self.entry.delete(0, tk.END)  # очищение поля ввода
        self.entry.focus_set()  # курсор в поле ввода

        # очищаем текстовое поле истории
        self.history_text.delete(1.0, tk.END)
        self.add_to_history("=== НОВАЯ ИГРА ===\n")
        self.add_to_history("Загадано 4-х значное число без повторяющихся цифр.\n")
        self.add_to_history("Введите свою догадку и нажмите 'ПРОВЕРИТЬ'!\n" + "=" * 50 + "\n")

    def add_to_history(self, text):  # добавление текста в историю
        self.history_text.insert(tk.END, text + "\n")
        self.history_text.see(tk.END)  # прокручиваем вниз
        
        # записываем в файл
        with open(self.history_file, 'a', encoding='utf-8') as f:
            f.write(text + "\n")

    def load_stats(self):  # загрузка статистики из файла
        if os.path.exists("game_stats.json"):
            try:
                with open("game_stats.json", 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
                logging.info("статистика загружена из файла")
            except:
                logging.warning("ошибка загрузки статистики")
                self.stats = {'games_played': 0, 'wins': 0, 'total_attempts': 0, 'best_attempts': 0}
        else:
            self.stats = {'games_played': 0, 'wins': 0, 'total_attempts': 0, 'best_attempts': 0}

    def save_stats(self):  # сохранение статистики в файл
        with open("game_stats.json", 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        logging.info("статистика сохранена")

    def show_stats(self):  # окно статистики
        stats_window = tk.Toplevel(self.root)
        stats_window.title("СТАТИСТИКА")
        stats_window.geometry("400x400")
        stats_window.resizable(False, False)

        # заголовок окна
        tk.Label(stats_window, text="СТАТИСТИКА ИГР", font=("Arial", 16, "bold")).pack(pady=10)

        # рамка статистики
        stats_frame = tk.Frame(stats_window)
        stats_frame.pack(pady=10, padx=20, fill=tk.BOTH)

        # вычисляем статистику
        games_played = self.stats.get('games_played', 0)
        wins = self.stats.get('wins', 0)
        losses = games_played - wins
        total_attempts = self.stats.get('total_attempts', 0)
        best_attempts = self.stats.get('best_attempts', 0)
        avg_attempts = total_attempts / games_played if games_played > 0 else 0
        win_percent = (wins / games_played * 100) if games_played > 0 else 0

        stats_text = (
            f"сыграно игр: {games_played}\n"
            f"побед: {wins}\n"
            f"поражений: {losses}\n"
            f"процент побед: {win_percent:.1f}%\n"
            f"среднее попыток: {avg_attempts:.1f}\n"
            f"лучший результат: {best_attempts} попыток"
        )

        tk.Label(stats_frame, text=stats_text, font=("Arial", 12), justify=tk.LEFT).pack(anchor=tk.W)

        # кнопки управления
        btn_frame = tk.Frame(stats_window)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="СБРОСИТЬ СТАТИСТИКУ",
                  command=self.reset_stats_confirmation,
                  font=("Arial", 12), bg="lightcoral").pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="ЗАКРЫТЬ",
                  command=lambda: (stats_window.destroy(), logging.info("окно статистики закрыто")),
                  font=("Arial", 12)).pack(side=tk.LEFT, padx=10)

        logging.info("открыто окно статистики")

    def reset_stats_confirmation(self):  # окно сброса статистики
        result = messagebox.askyesno(
            "СБРОС СТАТИСТИКИ",
            "обнулить всю статистику?"
        )

        if result:  # сброс статистики в исходные значения
            self.stats = {'games_played': 0, 'wins': 0, 'total_attempts': 0, 'best_attempts': 0}
            self.save_stats()  # сохраняем сброшенную статистику в файл
            logging.info("статистика сброшена пользователем")
            messagebox.showinfo("статистика", "статистика сброшена.")
        else:
            logging.info("сброс статистики отменён")

#настройка логирования
logging.basicConfig(
    filename='game.log', #куда сохранять лог
    level=logging.INFO, #стандартные информативные сообщения
    format='%(asctime)s - %(levelname)s - %(message)s', #время записи, уровень сообщения, текст сообщения
    encoding='utf-8' #язык
)

root = tk.Tk()  #создание гл.окна
game = BullsAndCowsGame(root)  #объект класса передаваемый в гл.окно 

root.protocol(
    "WM_DELETE_WINDOW",
    lambda: (
        logging.info("игра 'БЫКИ И КОРОВЫ' закрыта пользователем"), #записывает в лог, что пользователь закрыл приложение
        root.destroy() #закрывает окно и завершает работу программы
    )
)

root.mainloop()  #запуск гл. цикла окна
