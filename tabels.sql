CREATE TABLE "ksiazka"(
    "id_ksiazka" SERIAL NOT NULL,
    "tytul" VARCHAR(64) NOT NULL,
    "ile_egzemplarzy" INTEGER NOT NULL,
    "id_autor" INTEGER NOT NULL,
    "id_wydawnictwo" INTEGER NOT NULL,
    "id_dzial" INTEGER NOT NULL
);
ALTER TABLE
    "ksiazka" ADD PRIMARY KEY("id_ksiazka");
CREATE TABLE "autor"(
    "id_autor" SERIAL NOT NULL,
    "imie" VARCHAR(64) NOT NULL,
    "nazwisko" VARCHAR(64) NOT NULL
);
ALTER TABLE
    "autor" ADD PRIMARY KEY("id_autor");
CREATE TABLE "wydawnictwo"(
    "id_wydawnictwo" SERIAL NOT NULL,
    "nazwa" VARCHAR(64) NOT NULL
);
ALTER TABLE
    "wydawnictwo" ADD PRIMARY KEY("id_wydawnictwo");
CREATE TABLE "dzial"(
    "id_dzial" SERIAL NOT NULL,
    "nazwa" VARCHAR(64) NOT NULL
);
ALTER TABLE
    "dzial" ADD PRIMARY KEY("id_dzial");
CREATE TABLE "czytelnik"(
    "id_czytelnik" SERIAL NOT NULL,
    "imie" VARCHAR(64) NOT NULL,
    "nazwisko" VARCHAR(64) NOT NULL,
    "miasto" VARCHAR(64) NOT NULL,
    "adres" VARCHAR(64) NOT NULL,
    "kod_pocztowy" VARCHAR(64) NOT NULL,
    "login" VARCHAR(64) NOT NULL,
    "haslo" VARCHAR(64) NOT NULL
);
ALTER TABLE
    "czytelnik" ADD PRIMARY KEY("id_czytelnik");
CREATE TABLE "wypozyczenie"(
    "id_wypozyczenia" SERIAL NOT NULL,
    "data_wypozyczenia" DATE NOT NULL,
    "data_oddania" DATE NOT NULL,
    "id_czytelnik" INTEGER NOT NULL,
    "id_ksiazka" INTEGER NOT NULL
);
ALTER TABLE
    "wypozyczenie" ADD PRIMARY KEY("id_wypozyczenia");
CREATE TABLE "rezerwacja"(
    "id_rezerwacja" SERIAL NOT NULL,
    "wygasa" DATE NOT NULL,
    "id_czytelnik" INTEGER NOT NULL,
    "id_ksiazka" INTEGER NOT NULL
);
ALTER TABLE
    "rezerwacja" ADD PRIMARY KEY("id_rezerwacja");
ALTER TABLE
    "wypozyczenie" ADD CONSTRAINT "wypozyczenie_id_czytelnik_foreign" FOREIGN KEY("id_czytelnik") REFERENCES "czytelnik"("id_czytelnik");
ALTER TABLE
    "rezerwacja" ADD CONSTRAINT "rezerwacja_id_czytelnik_foreign" FOREIGN KEY("id_czytelnik") REFERENCES "czytelnik"("id_czytelnik");
ALTER TABLE
    "ksiazka" ADD CONSTRAINT "ksiazka_id_dzial_foreign" FOREIGN KEY("id_dzial") REFERENCES "dzial"("id_dzial");
ALTER TABLE
    "wypozyczenie" ADD CONSTRAINT "wypozyczenie_id_ksiazka_foreign" FOREIGN KEY("id_ksiazka") REFERENCES "ksiazka"("id_ksiazka");
ALTER TABLE
    "rezerwacja" ADD CONSTRAINT "rezerwacja_id_ksiazka_foreign" FOREIGN KEY("id_ksiazka") REFERENCES "ksiazka"("id_ksiazka");
ALTER TABLE
    "ksiazka" ADD CONSTRAINT "ksiazka_id_wydawnictwo_foreign" FOREIGN KEY("id_wydawnictwo") REFERENCES "wydawnictwo"("id_wydawnictwo");
ALTER TABLE
    "ksiazka" ADD CONSTRAINT "ksiazka_id_autor_foreign" FOREIGN KEY("id_autor") REFERENCES "autor"("id_autor");

