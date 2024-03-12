
CREATE VIEW book_info AS 
SELECT ksiazka.id_ksiazka, ksiazka.tytul, CONCAT(autor.imie,' ',autor.nazwisko) as autor, wydawnictwo.nazwa as nazwa_wydawnictwa, dzial.nazwa as nazwa_dzial, ksiazka.ile_egzemplarzy
FROM ksiazka
JOIN autor ON ksiazka.id_autor = autor.id_autor
JOIN wydawnictwo ON ksiazka.id_wydawnictwo = wydawnictwo.id_wydawnictwo
JOIN dzial ON ksiazka.id_dzial = dzial.id_dzial
WHERE ksiazka.ile_egzemplarzy >= 1;


CREATE VIEW reservation_view AS
SELECT ksiazka.tytul, ksiazka.id_ksiazka, CONCAT(autor.imie,' ',autor.nazwisko) as autor, rezerwacja.wygasa, rezerwacja.id_czytelnik, rezerwacja.id_rezerwacja, autor.id_autor, dzial.id_dzial, ksiazka.id_wydawnictwo
FROM ksiazka
JOIN autor ON ksiazka.id_autor = autor.id_autor
JOIN rezerwacja ON ksiazka.id_ksiazka = rezerwacja.id_ksiazka
JOIN czytelnik ON rezerwacja.id_czytelnik = czytelnik.id_czytelnik
JOIN dzial ON ksiazka.id_dzial = dzial.id_dzial;

CREATE VIEW rental_view AS
SELECT wypozyczenie.id_wypozyczenia, wypozyczenie.data_wypozyczenia, wypozyczenie.data_oddania, czytelnik.id_czytelnik, ksiazka.tytul, CONCAT(autor.imie,' ',autor.nazwisko) as autor, autor.id_autor, dzial.id_dzial, ksiazka.id_wydawnictwo
FROM wypozyczenie
JOIN czytelnik ON wypozyczenie.id_czytelnik = czytelnik.id_czytelnik
JOIN ksiazka ON wypozyczenie.id_ksiazka = ksiazka.id_ksiazka
JOIN autor ON ksiazka.id_autor = autor.id_autor
JOIN dzial ON ksiazka.id_dzial = dzial.id_dzial;

CREATE VIEW readers_view AS
SELECT czytelnik.imie, czytelnik.nazwisko, czytelnik.miasto, czytelnik.adres, czytelnik.kod_pocztowy, czytelnik.login, 
(SELECT COUNT(wypozyczenie.id_wypozyczenia) FROM wypozyczenie WHERE wypozyczenie.id_czytelnik = czytelnik.id_czytelnik) AS liczba_wypozyczen, 
(SELECT COUNT(DISTINCT rezerwacja.id_rezerwacja) FROM rezerwacja WHERE rezerwacja.id_czytelnik = czytelnik.id_czytelnik) AS liczba_rezerwacji
FROM czytelnik
WHERE czytelnik.login != 'admin'

CREATE VIEW reservation_view_for_admin AS
SELECT ksiazka.tytul, CONCAT(autor.imie,' ',autor.nazwisko) as autor, CONCAT(czytelnik.imie,' ',czytelnik.nazwisko) as czytelnik, rezerwacja.wygasa, rezerwacja.id_rezerwacja, czytelnik.login
FROM ksiazka
INNER JOIN autor  ON ksiazka.id_autor = autor.id_autor
INNER JOIN rezerwacja  ON ksiazka.id_ksiazka = rezerwacja.id_ksiazka
INNER JOIN czytelnik  ON rezerwacja.id_czytelnik = czytelnik.id_czytelnik;

CREATE VIEW rents_view_for_admin AS
SELECT ksiazka.tytul, CONCAT(autor.imie,' ',autor.nazwisko) as autor, CONCAT(czytelnik.imie,' ',czytelnik.nazwisko) as czytelnik, wypozyczenie.data_wypozyczenia, wypozyczenie.data_oddania, wypozyczenie.id_wypozyczenia, czytelnik.login
FROM ksiazka
INNER JOIN autor  ON ksiazka.id_autor = autor.id_autor
INNER JOIN wypozyczenie  ON ksiazka.id_ksiazka = wypozyczenie.id_ksiazka
INNER JOIN czytelnik  ON wypozyczenie.id_czytelnik = czytelnik.id_czytelnik


CREATE FUNCTION check_postal_code(p_postal_code VARCHAR)
RETURNS VARCHAR
LANGUAGE plpgsql
AS $$
BEGIN
  IF (SELECT regexp_matches(p_postal_code, '^[0-9]{2}-[0-9]{3}$'))[1] IS NOT NULL THEN
    RETURN 'Kod pocztowy jest prawidłowy.';
  ELSE
    RETURN 'Kod pocztowy jest nieprawidłowy.';
  END IF;
END;
$$;

CREATE OR REPLACE FUNCTION check_all_fields(p_field1 TEXT, p_field2 TEXT, p_field3 TEXT, p_field4 TEXT, p_field5 TEXT, p_field6 TEXT)
RETURNS TEXT
AS $$
BEGIN
    IF p_field1 = '' OR p_field2 = '' OR p_field3 = '' OR p_field4 = '' OR p_field5 = '' OR p_field6 = '' THEN
        RETURN 'Wszystkie pola muszą być uzupełnione';
    ELSE
        RETURN 'Wszystko jest w porządku';
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION check_login(p_username TEXT, p_password TEXT)
RETURNS BOOLEAN
AS $$
DECLARE
    result BOOLEAN;
BEGIN
    SELECT EXISTS (SELECT 1 FROM czytelnik WHERE login = p_username AND haslo = p_password) INTO result;
    RETURN result;
END;
$$ LANGUAGE plpgsql;
