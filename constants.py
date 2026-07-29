WHITE = True
BLACK = False
COLOR_TO_STRING = {WHITE: "White", BLACK: "Black"}

INITIAL_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

DIFF_TO_OPTION = {(-2): "[outvar, outvar]", (-1): "[outvar]", 0: "", 1: "[invar]", 2: "[invar, invar]"}
# For Latex, given level and preceding level of variation, and from there diff = level - preceding level,
# associates a diff value to the corresponding variation option

NAG_TO_SYMBOL = {
    "$1": "!",
    "$2": "?",
    "$3": "!!",
    "$4": "??",
    "$5": "!?",
    "$6": "?!",
    "$7": "□",

    # Position evaluations
    "$12": "=",
    "$11": "=",
    "$10": "=",
    "$13": "∞",
    "$14": "⩲",   # White is slightly better
    "$15": "⩱",   # Black is slightly better
    "$16": "±",   # White has a moderate advantage
    "$17": "∓",   # Black has a moderate advantage
    "$18": "+−",  # White has a decisive advantage
    "$19": "−+",  # Black has a decisive advantage
    "$20": "+-",  # White has a crushing advantage
    "$21": "-+",  # Black has a crushing advantage

    # Initiative / attack
    "$22": "⨀",   # White is in zugzwang
    "$23": "⨀",   # Black is in zugzwang
    "$36": "→",   # White has the initiative
    "$37": "→",   # Black has the initiative
    "$40": "↑",   # White has the attack
    "$41": "↑",   # Black has the attack

    # Compensation
    "$44": "=/∞", # White has compensation
    "$45": "∞/=", # Black has compensation

    # Development / center
    "$132": "⇆",  # Counterplay
    "$133": "⇆",
    "$138": "⟳",  # Time pressure

    # ChessPad
    "$140": "∆",
    "$141": "∇",
    "$142": "⌓",
    "$143": "<=",
    "$144": "==",
    "$145": "RR",
    "$146": "(N)",  # it should be N, but my code fails at parsing knights if this is the case
}

# To avoid Key Error, we add dummy entries
for i_gan in range(257):
    if f"${i_gan}" not in NAG_TO_SYMBOL.keys():
        NAG_TO_SYMBOL[f"${i_gan}"] = "∆"

SYMBOL_TO_NAG = {symbol: nag for nag, symbol in NAG_TO_SYMBOL.items()}

