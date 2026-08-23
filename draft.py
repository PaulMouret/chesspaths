from global_utils import clean_chess_in_text


if __name__ == "__main__":
    my_string = r"Après cela les Blancs veulent jouer Nd4-c6, O-O et Re1. " \
                r"Si les Noirs jouent ...De8, ils ne pourront pas répliquer à Cc3 par l'habituel ...c6/d5. " \
                r"Contrairement à la variante 11...O-O, la variante 11...e5 permet donc de répliquer à " \
                r"12.c4 par 12...e4."
    res = clean_chess_in_text(my_string)
    print(res)
