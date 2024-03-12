import PySimpleGUI as sg
import data
import psycopg2
import datetime
import re
from psycopg2 import OperationalError

def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection

connection = create_connection(data.db_name,data.db_login,data.db_pass, data.db_host, data.db_port)


def check_login(user, userPass):
    cursor = connection.cursor()
    cursor.execute("SELECT check_login(%s, %s)", (user, userPass))
    result = cursor.fetchone()[0]
    connection.commit()
    if result:
        return True
    else:
        return False

def check_fields(field1,field2,field3,field4,field5,field6):
    cursor = connection.cursor()
    cursor.execute(f"SELECT check_all_fields('{field1}', '{field2}','{field3}','{field4}','{field5}','{field6}')")
    result = cursor.fetchone()[0]
    connection.commit()
    return result



def check_postal_code(postal_code):
    cursor = connection.cursor()
    cursor.execute(f"SELECT check_postal_code('{postal_code}')")
    result = cursor.fetchone()[0]
    connection.commit()
    return result

def login():
    layout = [[sg.Text('Login'), sg.InputText()],
              [sg.Text('Haslo'), sg.InputText(password_char='*')],
              [sg.Button('Zaloguj'), sg.Button('Zarejestruj')]
             ]

    window = sg.Window('Logowanie', layout)

    while True:
        event, values = window.read()
        if event in (None, 'Exit'):
            break
        if event == 'Zaloguj':
            global user, userPass
            user = values[0]
            userPass = values[1]
            if check_login(user, userPass):
                window.close()
                return True
            else:
                sg.popup("Nie ma takiego użytkownika")

        if event == 'Zarejestruj':
            layout_register = [[sg.Text('Rejestracja')],
                            [sg.Text('Login'), sg.InputText()],
                            [sg.Text('Haslo'), sg.InputText(password_char='*')],
                            [sg.Text('Imie'), sg.InputText()],
                            [sg.Text('Nazwisko'), sg.InputText()],
                            [sg.Text('Miasto'), sg.InputText()],
                            [sg.Text('Adres'), sg.InputText()],
                            [sg.Text('Kod pocztowy'), sg.InputText()],
                            [sg.Button('Rejestruj'), sg.Button('Anuluj')]
                        ]


            window_register = sg.Window('Rejestracja', layout_register)
            while True:   
                event, values = window_register.read()                 
                if event in (None, 'Exit'):
                    break
                if event == 'Rejestruj':   
                    try:                 
                        if check_fields(values[0],values[1],values[2],values[3],values[4],values[5]) == 'Wszystkie pola muszą być uzupełnione':
                            sg.popup('Wszystkie pola muszą być uzupełnione')
                        elif check_postal_code(values[6]) == "Kod pocztowy jest nieprawidłowy.":
                            sg.popup('Kod pocztowy jest nieprawidłowy. Proszę podać kod w formacie "**-***", gdzie * to cyfra')
                        else:
                            cursor = connection.cursor()
                            cursor.execute(f"INSERT INTO czytelnik (login, haslo, imie, nazwisko, miasto, adres, kod_pocztowy) VALUES ('{values[0]}', '{values[1]}', '{values[2]}', '{values[3]}', '{values[4]}', '{values[5]}', '{values[6]}')")
                            connection.commit()
                            window_register.close()
                    except psycopg2.DatabaseError as e:
                        connection.rollback()
                        if e.pgcode == '23505':
                            sg.popup("Login jest już zajęty.")
                        else:
                            cursor = connection.cursor()
                            cursor.execute(f"INSERT INTO czytelnik (login, haslo, imie, nazwisko, miasto, adres, kod_pocztowy) VALUES ('{values[0]}', '{values[1]}', '{values[2]}', '{values[3]}', '{values[4]}', '{values[5]}', '{values[6]}')")
                            connection.commit()
                            window_register.close()
                if event == 'Anuluj':
                    window_register.close()

##################### GET FUNCTIONS ##############################################
def get_user_id(user, userPass):
    cursor = connection.cursor()
    cursor.execute(f"SELECT id_czytelnik FROM czytelnik WHERE login = '{user}' AND haslo = '{userPass}'")
    id = cursor.fetchall()
    connection.commit()
    return id[0][0]

def get_book_id_by_tittle_and_autor(tittle, autor):
    cursor = connection.cursor()
    cursor.execute(f"SELECT id_ksiazka FROM book_info WHERE tytul = '{tittle}' AND autor = '{autor}'")
    book_id = cursor.fetchall()
    connection.commit()
    return book_id[0][0]

def get_reservation_id(tittle, autor, user_id):
    cursor = connection.cursor()
    cursor.execute(f"SELECT id_rezerwacja FROM reservation_view WHERE tytul = '{tittle}' AND autor = '{autor}' AND id_czytelnik = {user_id}")
    reservation_id = cursor.fetchall()
    connection.commit()
    return reservation_id[0][0]

def get_rent_id(tittle, autor, user_id):
    cursor = connection.cursor()
    cursor.execute(f"SELECT id_wypozyczenia FROM rental_view WHERE tytul = '{tittle}' AND autor = '{autor}' AND id_czytelnik = {user_id}")
    rent_id = cursor.fetchall()
    connection.commit()
    return rent_id[0][0]

def get_number_of_reservation(user):
    if user == 'admin':
        cursor = connection.cursor()
        cursor.execute(f"SELECT SUM(liczba_rezerwacji) FROM  readers_view")
        number = cursor.fetchall()
        connection.commit()
    else:
        cursor = connection.cursor()
        cursor.execute(f"SELECT liczba_rezerwacji FROM  readers_view WHERE login = '{user}'")
        number = cursor.fetchall()
        connection.commit()
    return number[0][0]

def get_number_of_rent(user):
    if user == 'admin':
        cursor = connection.cursor()
        cursor.execute(f"SELECT SUM(liczba_wypozyczen) FROM  readers_view")
        number = cursor.fetchall()
        connection.commit()
    else:
        cursor = connection.cursor()
        cursor.execute(f"SELECT liczba_wypozyczen FROM  readers_view WHERE login = '{user}'")
        number = cursor.fetchall()
        connection.commit()
    return number[0][0]

def get_number_of_users():
    cursor = connection.cursor()
    cursor.execute(f"SELECT count(*) FROM  readers_view")
    number = cursor.fetchall()
    connection.commit()
    return number[0][0]    


##################### UPDATE FUNCTIONS ##############################################
def update_books_piece_value(book_id):
    cursor = connection.cursor()
    cursor.execute(f"UPDATE ksiazka SET ile_egzemplarzy = ile_egzemplarzy - 1 WHERE id_ksiazka = {book_id}")
    connection.commit()


##################### SHOW FUNCTIONS ##############################################

def show_books():
        cursor = connection.cursor()
        cursor.execute(f"SELECT tytul, autor, nazwa_wydawnictwa, nazwa_dzial, ile_egzemplarzy FROM book_info;")
        books = cursor.fetchall()
        return books

def show_reservations(user_id):
    cursor = connection.cursor()
    cursor.execute(f" SELECT tytul, autor, wygasa FROM reservation_view WHERE id_czytelnik = {user_id};")
    reservations = cursor.fetchall()
    return reservations
    
def show_rents(user_id):
    cursor = connection.cursor()
    cursor.execute(f"SELECT tytul, autor, data_wypozyczenia, data_oddania FROM rental_view WHERE id_czytelnik = {user_id};")
    rents = cursor.fetchall()
    return rents

def show_users():
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM readers_view")
    readers = cursor.fetchall()
    connection.commit()
    return readers

def show_reservations_admin():
    cursor = connection.cursor()
    cursor.execute(f"SELECT tytul, autor, czytelnik, wygasa, login FROM reservation_view_for_admin")
    reservations = cursor.fetchall()
    connection.commit()    
    return reservations

def show_rents_admin():
    cursor = connection.cursor()
    cursor.execute(f"SELECT tytul, autor, czytelnik, data_wypozyczenia, data_oddania, login FROM rents_view_for_admin")
    rents = cursor.fetchall()
    connection.commit()    
    return rents

##################### REST FUNCTIONS ##############################################
def search_books(search_criteria):
    cursor = connection.cursor()
    cursor.execute(f"SELECT tytul, autor FROM book_info WHERE tytul LIKE '%{search_criteria}%' OR autor LIKE '%{search_criteria}%';")
    books = cursor.fetchall()
    return books

def reserve_book(book_id, user_id):
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO rezerwacja (id_ksiazka, id_czytelnik, wygasa) VALUES ({book_id}, {user_id}, '{datetime.date.today()+datetime.timedelta(days=7)}')")
    connection.commit()
    update_books_piece_value(book_id)
    print("Książka zarezerwowana")

def rent_book(reservation_id, user_id):
    cursor = connection.cursor()
    cursor.execute(f"SELECT id_ksiazka FROM reservation_view WHERE id_rezerwacja = {reservation_id}")
    book_id = cursor.fetchall()[0][0]
    connection.commit()

    cursor.execute(f"INSERT INTO wypozyczenie (id_ksiazka, id_czytelnik, data_wypozyczenia, data_oddania) VALUES ({book_id}, {user_id}, '{datetime.date.today()}', '{datetime.date.today()+datetime.timedelta(days=30)}')")
    connection.commit()

    cursor.execute(f"DELETE FROM rezerwacja WHERE id_rezerwacja = {reservation_id}")
    connection.commit()
    print("Książka wypozyczona")

def find_book(criteria):
    cursor = connection.cursor()
    cursor.execute(f"SELECT id_ksiazka FROM ksiazka WHERE tytul = '{criteria[0][0]}' AND id_autor = {criteria[0][1]} AND id_dzial = {criteria[0][2]} AND id_wydawnictwo = {criteria[0][3]}")
    book_id = cursor.fetchall()
    connection.commit()
    if(book_id):
        return book_id
    else:
        False

def add_book(tittle, name, surname, publisher, section):
    cursor = connection.cursor()
    cursor.execute(f"SELECT id_autor FROM autor WHERE imie = '{name}' AND nazwisko = '{surname}';")
    autor_id = cursor.fetchall()
    connection.commit()
    if(not autor_id):  
        cursor.execute(f"INSERT INTO autor (imie, nazwisko) VALUES ('{name}','{surname}')")
        connection.commit()
        cursor.execute(f"SELECT id_autor FROM autor WHERE imie = '{name}' AND nazwisko = '{surname}';")
        autor_id = cursor.fetchall()
        connection.commit()

    cursor.execute(f"SELECT id_wydawnictwo FROM wydawnictwo WHERE nazwa = '{publisher}';")
    publisher_id = cursor.fetchall()
    connection.commit()
    if(not publisher_id):  
        cursor.execute(f"INSERT INTO wydawnictwo (nazwa) VALUES ('{publisher}');")
        connection.commit()
        cursor.execute(f"SELECT id_wydawnictwo FROM wydawnictwo WHERE nazwa = '{publisher}';")
        publisher_id = cursor.fetchall()
        connection.commit()

    cursor.execute(f"SELECT id_dzial FROM dzial WHERE nazwa = '{section}';")
    section_id = cursor.fetchall()
    connection.commit()
    if(not section_id):  
        cursor.execute(f"INSERT INTO dzial (nazwa) VALUES ('{section}');")
        connection.commit()
        cursor.execute(f"SELECT id_dzial FROM dzial WHERE nazwa = '{section}';")
        section_id = cursor.fetchall()
        connection.commit()

    cursor.execute(f"SELECT id_ksiazka FROM ksiazka WHERE tytul = '{tittle}' AND id_autor = {autor_id[0][0]} AND id_dzial = {section_id[0][0]} AND id_wydawnictwo = {publisher_id[0][0]}")
    book_id = cursor.fetchall()
    connection.commit()
    if(book_id):
        cursor.execute(f"UPDATE ksiazka SET ile_egzemplarzy = ile_egzemplarzy + 1 WHERE id_ksiazka = {book_id[0][0]}")
        print("Dodano egzemplarz")
    else:
        cursor.execute(f"INSERT INTO ksiazka (tytul, id_autor, id_dzial, id_wydawnictwo, ile_egzemplarzy) VALUES('{tittle}', {autor_id[0][0]},{section_id[0][0]},{publisher_id[0][0]}, {1})")
        print("Dodano ksiazke")

    connection.commit()

##################### DELETE FUNCTIONS ##############################################
def delete_rent(rent_id):
    cursor = connection.cursor()
    cursor.execute(f"SELECT tytul, id_autor, id_dzial, id_wydawnictwo FROM rental_view WHERE id_wypozyczenia = {rent_id}")
    book_info = cursor.fetchall()
    connection.commit()
    book_id = find_book(book_info)
    if(book_id):
        cursor.execute(f"UPDATE ksiazka SET ile_egzemplarzy = ile_egzemplarzy + 1 WHERE id_ksiazka = {book_id[0][0]}")
    else:
        cursor.execute(f"INSERT INTO ksiazka (tytul, id_autor, id_dzial, id_wydawnictwo, ile_egzemplarzy) VALUES('{book_info[0][0]}', {book_info[0][3]},{book_info[0][2]},{book_info[0][3]}, {1})")

    connection.commit()
    cursor.execute(f"DELETE FROM wypozyczenie WHERE id_wypozyczenia = {rent_id}")
    connection.commit()
    print("Książka oddana")

def delete_reservation(reservation_id):
    cursor = connection.cursor()
    cursor.execute(f"SELECT tytul, id_autor, id_dzial, id_wydawnictwo FROM reservation_view WHERE id_rezerwacja = {reservation_id}")
    book_info = cursor.fetchall()
    connection.commit()
    book_id = find_book(book_info)
    if(book_id):
        cursor.execute(f"UPDATE ksiazka SET ile_egzemplarzy = ile_egzemplarzy + 1 WHERE id_ksiazka = {book_id[0][0]}")
    else:
        cursor.execute(f"INSERT INTO ksiazka (tytul, id_autor, id_dzial, id_wydawnictwo, ile_egzemplarzy) VALUES('{book_info[0][0]}', {book_info[0][3]},{book_info[0][2]},{book_info[0][3]}, {1})")

    connection.commit()
    cursor.execute(f"DELETE FROM rezerwacja WHERE id_rezerwacja = {reservation_id}")
    connection.commit()
    print("Rezerwacja usunieta")


##################### GUI FUNCTION ##############################################
def GUI():
    if(login()):

        # Szukanie id zalogowanego czytelnika
        user_id = get_user_id(user, userPass)

        # Tworzenie glownego okna
        if user_id==1: 
            layout = [[sg.Text(f"Witaj {user}!")],[sg.Button('Ksiazki'), sg.Button('Rezerwacje'), sg.Button('Wypozyczenia'),sg.Button('Czytelnicy')], [sg.Button('Wyloguj')]]
        else:
            layout = [[sg.Text(f"Witaj {user}!")],[sg.Button('Ksiazki'), sg.Button('Rezerwacje'), sg.Button('Wypozyczenia'),sg.Button('Rezerwuj')], [sg.Button('Wyloguj')]]

        window = sg.Window('Biblioteka', layout, size=(1000,600))

        # Obsluga przyciskow
        while True:
            event, values = window.read()
            if event in (None, 'Exit'):
                break
            if event == 'Ksiazki':
                # Po kliknieciu przyciski "Ksiazki" wyswietli nam sie tabela z informacjami o ksiazkach w bazie danych
                # Sprawdzamy czy zalogowany uzytkownik jest adminem i dostosowujemy menu pod uzytkownika
                if user_id == 1:            
                    books_table = sg.Table(values=show_books(), headings=['Tytul', 'Autor','Wydawnictwo', 'Dzial', 'Ilosc'], auto_size_columns=True, num_rows=10, key='books_table', enable_events=True)
                    layout = [[books_table], [sg.Button('Dodaj')], [sg.Button('Powrot')]]
                else:
                    books_table = sg.Table(values=show_books(), headings=['Tytul', 'Autor','Wydawnictwo', 'Dzial', 'Ilosc'],
                                auto_size_columns=True, num_rows=10, key='books_table', enable_events=False)
                    layout = [[books_table], [sg.Button('Powrot')]]
                
                window.close()
                window = sg.Window('Ksiazki', layout, size=(1000,600))
                
                # Obsluga przyciskow i zdarzen w okienku "Ksiazki"
                while True:
                    event, values = window.read()
                    if event in (None, 'Exit', 'Powrot'):
                        break
                    if event == 'Dodaj':
                        layout = [[sg.Text('Tytul'), sg.InputText()],
                                [sg.Text('Imiona autora'), sg.InputText()],
                                [sg.Text('Nazwisko autora'), sg.InputText()],
                                [sg.Text('Wydawnictwo'), sg.InputText()],
                                [sg.Text('Dzial'), sg.InputText()],
                                [sg.Button('Dodaj'), sg.Button('Powrot')]
                        ]
                        window.close()                      
                        window = sg.Window('Dodaj ksiazke', layout)
                        
                        event, values = window.read()    
                        tittle = values[0]
                        name = values[1]
                        surname = values[2]
                        publisher = values[3]
                        section = values[4]
                        while True:
                            event, values = window.read()
                            if event in (None, 'Exit', 'Powrot'):
                                break
                            if event == 'Dodaj':
                                if not values[0] or not values[1] or not values[2] or not values[3] or not values[4]:
                                    sg.popup('Wszystkie pola muszą być uzupełnione')
                                else:
                                    add_book(tittle, name, surname, publisher, section)
                                    sg.popup('Dodano ksiazke')
                    if event == 'books_table' and values['books_table'] != None:
                        clicked_row = values['books_table'][0]
                        selected_row = show_books()[clicked_row]
                        if sg.popup_yes_no(f'Czy chcesz usunac egzemplarz {selected_row[0]} {selected_row[1]}?') == 'Yes':
                            book_id = get_book_id_by_tittle_and_autor(selected_row[0], selected_row[1])
                            update_books_piece_value(book_id)
                            print('Usunieto egzemplarz')
                            
            if event == 'Rezerwuj':
                layout = [
                    [sg.Text('Wyszukaj:'), sg.Input(key='search_bar', enable_events=True)],
                    [sg.Listbox([], size=(None, 10), enable_events=True, key='list_books', expand_x=True)],
                    [sg.Button('Powrot')]
                ]
                window.close()
                window = sg.Window('Rezerwacje', layout, size=(1000, 600))
                while True:
                    event, values = window.read()
                    if event in (None, 'Powrot'):
                        break
                    if values['search_bar'] != None:
                        search = values['search_bar']
                        new_values = search_books(search)
                        window['list_books'].update(new_values)
                    if event == 'list_books' and len(values['list_books']):
                        if sg.popup_yes_no(f"Czy na pewno chcesz zarezerwować {values['list_books'][0]}?") == 'Yes':
                            book_id = get_book_id_by_tittle_and_autor(values['list_books'][0][0],values['list_books'][0][1])
                            reserve_book(book_id, user_id)
            if event == 'Rezerwacje':
                if user_id == 1:
                    reservation_table = sg.Table(values=show_reservations_admin(), headings=['Tytul', 'Autor','Czytelnik','Wygasa'], auto_size_columns=True, num_rows=10, key='reservation_table', enable_events=True)
                    layout = [[reservation_table],[sg.Text(f'Liczba rezerwacji {get_number_of_reservation(user)}')] ,[sg.Button('Powrot')]]
                    window.close()
                    window = sg.Window('Rezerwacje', layout, size=(1000,600))
                    while True:
                        event, values = window.read()
                        if event in (None, 'Exit'):
                            break
                        if event == 'reservation_table' and values['reservation_table'] != None:
                            clicked_row = values['reservation_table'][0]
                            selected_row = show_reservations_admin()[clicked_row]
                            if(sg.popup_yes_no(f'Usunac rezerwacje ksaizki {selected_row[0]} {selected_row[1]} czytelnika {selected_row[2]}?')) == 'Yes':
                                cursor = connection.cursor()
                                cursor.execute(f"SELECT id_rezerwacja FROM reservation_view_for_admin WHERE login = '{selected_row[4]}'")
                                reservation_id = cursor.fetchall()[0][0]
                                connection.commit()
                                delete_reservation(reservation_id)
                        if event =='Powrot':
                            break
                else:                
                    reservation_table = sg.Table(values=show_reservations(user_id), headings=['Tytul', 'Autor','Wygasa'], auto_size_columns=True, num_rows=10, key='reservation_table', enable_events=True)
                    layout = [[reservation_table], [sg.Text(f'Liczba rezerwacji: {get_number_of_reservation(user)}')] ,[sg.Button('Powrot')]]
                    window.close()
                    window = sg.Window('Rezerwacje', layout, size=(1000,600))
                    while True:
                        event, values = window.read()
                        if event in (None, 'Exit'):
                            break
                        if event == 'reservation_table' and values['reservation_table'] != None:
                            clicked_row = values['reservation_table'][0]
                            selected_row = show_reservations(user_id)[clicked_row]
                            if(sg.popup_yes_no(f'Odebrales {selected_row[0]} {selected_row[1]}?')) == 'Yes':
                                reservation_id = get_reservation_id(selected_row[0], selected_row[1], user_id)
                                rent_book(reservation_id, user_id)
                        if event =='Powrot':
                            break

            if event == 'Wypozyczenia':
                if user_id == 1:
                    rents_table = sg.Table(values=show_rents_admin(), headings=['Tytul', 'Autor','Czytelnik', 'Data wypozyczenia', 'Data oddania'], auto_size_columns=True, num_rows=10, key='rents_table', enable_events=True)
                    layout = [[rents_table], [sg.Text(f'Liczba wypozyczen: {get_number_of_rent(user)}')],[sg.Button('Powrot')]]
                    window.close()
                    window = sg.Window('Wypozyczenia', layout, size=(1000,600))
                    while True:
                        event, values = window.read()
                        if event in (None, 'Exit'):
                            break
                        if event == 'rents_table' and values['rents_table'] != None:
                            clicked_row = values['rents_table'][0]
                            selected_row = show_rents_admin()[clicked_row]
                            if(sg.popup_yes_no(f'Usunac wypozyczenie {selected_row[0]} {selected_row[1]} czytelnika {selected_row[2]}?')) == 'Yes':
                                cursor = connection.cursor()
                                cursor.execute(f"SELECT id_wypozyczenia FROM rents_view_for_admin WHERE login = '{selected_row[5]}'")
                                rent_id = cursor.fetchall()[0][0]
                                connection.commit()
                                delete_rent(rent_id)
                        if event =='Powrot':
                            break
                else:
                    rents_table = sg.Table(values=show_rents(user_id), headings=['Tytul', 'Autor','Data wypozyczenia','Data oddania'], auto_size_columns=True, num_rows=10, key='rents_table', enable_events=True)
                    layout = [[rents_table],[sg.Text(f'Liczba wypozyczen: {get_number_of_rent(user)}')], [sg.Button('Powrot')]]
                    window.close()
                    window = sg.Window('Wypozyczenia', layout, size=(1000,600))
                    while True:
                        event, values = window.read()
                        if event in (None, 'Exit'):
                            break
                        if event == 'rents_table' and values['rents_table'] != None:
                            clicked_row = values['rents_table'][0]
                            selected_row = show_rents(user_id)[clicked_row]
                            if(sg.popup_yes_no(f'Oddales {selected_row[0]} {selected_row[1]}?')) == 'Yes':
                                rent_id = get_rent_id(selected_row[0], selected_row[1], user_id)
                                delete_rent(rent_id)
                        if event =='Powrot':
                            break
            if event == 'Czytelnicy':
                readers_table = sg.Table(values=show_users(), headings=['Imie', 'Nazwisko','Miasto', 'Adres', 'Kod pocztowy', 'Login', 'Wypozyczenia', 'Rezerwacje'], auto_size_columns=True, num_rows=10, key='readers_table', enable_events=True)
                layout = [[readers_table],[sg.Text(f'Liczba czytelników: {get_number_of_users()}')], [sg.Button('Powrot')]]
                window.close()
                window = sg.Window('Czytelnicy', layout, size=(1000,600))

            if event == 'Powrot':
                window.close()
                if user_id==1: 
                    layout = [[sg.Text(f"Witaj {user}!")],[sg.Button('Ksiazki'), sg.Button('Rezerwacje'), sg.Button('Wypozyczenia'),sg.Button('Czytelnicy')], [sg.Button('Wyloguj')]]
                else:
                    layout = [[sg.Text(f"Witaj {user}!")],[sg.Button('Ksiazki'), sg.Button('Rezerwacje'), sg.Button('Wypozyczenia'),sg.Button('Rezerwuj')], [sg.Button('Wyloguj')]]
                window = sg.Window('Biblioteka', layout, size=(1000,600))
            if event == 'Wyloguj':
                window.close()
                GUI()

        window.close()


GUI()
