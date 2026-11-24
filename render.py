#!/usr/bin/env python3
"""news-image-20261124 — dense newspaper front page renderer.

Renders THE WORLD IN ONE DAY for Tuesday 24 November 2026 as a
1024x1024 RGB PNG. Pure Python stdlib + Pillow, no network at render
time, fully deterministic (fixed strings, fixed geometry, no clock).
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (178, 34, 34)
NAVY = (24, 36, 64)
GREY = (90, 86, 78)
LINE = (120, 112, 96)
CARD = (255, 252, 244)
MAPSEA = (214, 228, 235)
LAND = (196, 205, 178)
GOLD = (176, 132, 30)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS_O = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, font, width):
    """Greedy word wrap returning a list of lines that fit `width` px."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, font, width, leading, color=INK, max_lines=None):
    """Draw wrapped paragraph; return y just below last line."""
    lines = wrap(d, text, font, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=font, fill=color)
        y += leading
    return y


def hline(d, x0, x1, y, color=INK, width=1):
    d.line([(x0, y), (x1, y)], fill=color, width=width)


def box(d, x, y, w, h, fill=None, outline=None, width=1):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=fill, outline=outline, width=width)


# ---------------------------------------------------------------- stories
# certainty: R = reported, C = claim, F = forecast / scheduled
LEADS = [
    dict(n=1, kicker="TECH  •  THE LEAD STORY", region="AMERICAS",
         head="Huang is back: Nvidia board reinstates its CEO",
         body=("Nvidia reinstated Jensen Huang as chief executive on Monday after "
               "President Donald Trump pressed the board, saying Huang posed no "
               "national security risk. Shares leapt 33 percent in early trading."),
         cert="R", icon="chip", lon=-122.0, lat=37.4),
    dict(n=2, kicker="CLIMATE  •  ANTALYA", region="MIDDLE EAST",
         head="COP31 in ruins as talks end with no deal",
         body=("The COP31 climate summit collapsed after more than 190 countries "
               "failed to agree a final pact, because the draft never mentioned "
               "fossil fuels. Erdogan said the talks laid groundwork for more talks."),
         cert="R", icon="globe", lon=30.7, lat=36.9),
    dict(n=3, kicker="SECURITY  •  NATO'S EASTERN FLANK", region="EUROPE",
         head="NATO sends AWACS jets to Poland after missile scare",
         body=("NATO will deploy AWACS early-warning aircraft to Poland after three "
               "Russian Kh-101 missiles landed there on Friday. Germany warned "
               "Russia could put a nuclear weapon in space within 60 days."),
         cert="R", icon="radar", lon=19.0, lat=52.0),
]

GRID = [
    dict(n=4, kicker="WAR  •  LIBYA", region="AFRICA",
         head="Ukraine sinks Russian warship off Libya",
         body="Kyiv says its drones sank a Russian corvette in Benghazi port.",
         cert="C", icon="ship", lon=20.1, lat=32.1),
    dict(n=5, kicker="GULF  •  SANCTIONS", region="MIDDLE EAST",
         head="Iran vows to fight US naval blockade",
         body="Tehran says it will use every tool against the blockade.",
         cert="R", icon="shield", lon=51.4, lat=35.7),
    dict(n=6, kicker="USA  •  IOWA", region="AMERICAS",
         head="Trump halts toxic blast in Iowa",
         body="The Army pauses detonation of a lead azide stockpile.",
         cert="R", icon="flame", lon=-93.6, lat=41.9),
    dict(n=7, kicker="DISASTER  •  BANTEN", region="ASIA-PACIFIC",
         head="24 dead in Indonesia candy factory fire",
         body="Rescuers search the wreckage for about 30 missing workers.",
         cert="R", icon="factory", lon=106.1, lat=-6.1),
    dict(n=8, kicker="EU  •  SANCTIONS", region="EUROPE",
         head="EU plans new Russia sanctions",
         body="Banks, crypto and sports events are in the new package.",
         cert="R", icon="scale", lon=4.4, lat=50.8),
    dict(n=9, kicker="MARKETS  •  REBOUND", region="AMERICAS",
         head="Stocks rally as the AI panic eases",
         body="S and P futures rise 2 percent and Nasdaq futures 2.8 percent.",
         cert="R", icon="chart", lon=-74.0, lat=40.7),
    dict(n=10, kicker="USA  •  CONGRESS", region="AMERICAS",
         head="Democrats take House with 258 seats",
         body="Their majority is the largest since 1992, reports say.",
         cert="R", icon="ballot", lon=-77.0, lat=38.9),
    dict(n=11, kicker="SPORT  •  FOOTBALL", region="EUROPE",
         head="UK to host the 2035 Women's World Cup",
         body="FIFA confirms England, Scotland, Wales and N. Ireland.",
         cert="R", icon="trophy", lon=-0.1, lat=51.5),
    dict(n=12, kicker="SPORT  •  CHESS", region="EUROPE",
         head="Gukesh begins title defence in Geneva",
         body="The world champion faces Sindarov from today in Geneva.",
         cert="F", icon="chess", lon=6.1, lat=46.2),
    dict(n=13, kicker="SPORT  •  CRICKET", region="ASIA-PACIFIC",
         head="India and New Zealand draw first Test",
         body="The visitors fight back to save the match in Wellington.",
         cert="R", icon="bat", lon=174.8, lat=-41.3),
    dict(n=14, kicker="HEALTH  •  BRITAIN", region="EUROPE",
         head="UK starts huge AI breast screening trial",
         body="The study is billed as the largest of its kind in the world.",
         cert="R", icon="cross", lon=-1.3, lat=51.8),
    dict(n=15, kicker="TECH  •  CYBER", region="AMERICAS",
         head="CrowdStrike buys Zscaler in 40bn euro deal",
         body="The cybersecurity giants merge in a 40 billion euro deal.",
         cert="R", icon="deal", lon=-97.7, lat=30.3),
]

ALSO = [
    (16, "12,000 leave Manchester concert after irritant scare."),
    (17, "Settler arson hits five West Bank villages."),
    (18, "Israeli strikes kill three in Gaza, incl. UNRWA worker."),
    (19, "Oxfam: Gaza poisoned for decades by war contamination."),
    (20, "Trump favours Iran strikes after New Year if no deal."),
    (21, "EU and Indonesia sign a trade deal cutting most tariffs."),
    (22, "Modi opens AI centre at IIT Patna and research park."),
    (23, "India and China hold military talks in Arunachal."),
    (24, "Prabowo names two candidates to replace vice-president."),
    (25, "Germany to use Kyiv's Delta battle system, says Pistorius."),
    (26, "Finland summons Russia's envoy over reckless actions."),
    (27, "Cyprus expels two Russian diplomats in intelligence row."),
    (28, "South Korea education minister quits over AI exam rules."),
    (29, "Waymo pulls driverless taxis from every US freeway."),
    (30, "Democrats plan 12 debates for 2028, first in June."),
    (31, "World court: Myanmar committed genocide on Rohingya."),
    (32, "Davis Cup Final 8 begins today in Bologna, Italy."),
    (33, "Champions League: Arsenal v Dortmund, Man City v Napoli."),
    (34, "NBA Cup tonight: Magic, Wizards and Nuggets in action."),
    (35, "Monday Night Football: Cincinnati visit Washington."),
    (36, "LEGO to build 1bn euro factory in Portugal, 1,000 jobs."),
]

KPIS = [
    ("+33%", "NVIDIA SHARES"),
    ("+6%", "NASDAQ RALLY"),
    ("258", "DEMOCRAT HOUSE SEATS"),
    ("24", "DEAD IN BANTEN FIRE"),
    ("46", "COP31 DECISIONS ADOPTED"),
    ("12,000", "EVACUATED IN MANCHESTER"),
]

REGIONS = [
    ("EUROPE", 12, (24, 36, 64)),
    ("AMERICAS", 9, (178, 34, 34)),
    ("ASIA-PACIFIC", 8, (176, 132, 30)),
    ("MIDDLE EAST", 6, (34, 110, 80)),
    ("AFRICA", 1, (110, 70, 130)),
]

TIMELINE = [
    ("00:34", "UK AI breast screening study"),
    ("06:20", "European markets open"),
    ("12:15", "Dow Jones futures rally"),
    ("14:00", "Nvidia shares leap 33%"),
    ("16:30", "Huang returns to Nvidia HQ"),
    ("19:00", "Erdogan: COP31 groundwork"),
]

# Rough continent outlines (lon, lat) for the stylised world map.
CONTINENTS = [
    # North America
    [(-168, 66), (-158, 58), (-140, 60), (-130, 54), (-125, 49), (-124, 40),
     (-120, 34), (-114, 29), (-110, 24), (-105, 20), (-97, 16), (-92, 14),
     (-86, 12), (-83, 9), (-79, 9), (-81, 13), (-84, 16), (-87, 21),
     (-90, 21), (-91, 19), (-97, 26), (-93, 30), (-89, 30), (-84, 30),
     (-81, 26), (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 45),
     (-65, 44), (-60, 47), (-55, 47), (-60, 52), (-65, 58), (-68, 58),
     (-78, 62), (-85, 66), (-92, 66), (-95, 69), (-110, 68), (-125, 70),
     (-140, 70), (-155, 71), (-165, 68)],
    # Greenland
    [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68), (-22, 70),
     (-25, 74), (-32, 76), (-45, 76), (-58, 74), (-62, 70)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-68, -55),
     (-65, -55), (-65, -48), (-62, -41), (-57, -38), (-52, -33), (-48, -28),
     (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
     (-50, 0), (-52, 4), (-55, 6), (-60, 8), (-65, 10), (-70, 12), (-75, 11)],
    # Africa
    [(-17, 15), (-16, 20), (-15, 27), (-10, 31), (-6, 35), (0, 36), (10, 37),
     (11, 34), (19, 32), (25, 32), (30, 31), (32, 31), (34, 28), (35, 24),
     (37, 20), (39, 15), (41, 11), (43, 11), (48, 11), (51, 12), (51, 10),
     (46, 5), (41, 0), (40, -5), (40, -10), (38, -15), (36, -20), (33, -26),
     (28, -33), (20, -35), (17, -32), (15, -27), (12, -18), (13, -12),
     (12, -6), (9, -1), (9, 4), (-8, 4), (-13, 8), (-17, 12)],
    # Eurasia
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50),
     (0, 51), (3, 53), (5, 53), (8, 57), (10, 59), (5, 60), (10, 62),
     (12, 65), (18, 69), (25, 71), (30, 70), (35, 67), (40, 67), (45, 68),
     (55, 69), (65, 69), (70, 72), (80, 73), (90, 75), (100, 76), (110, 74),
     (120, 73), (130, 72), (140, 72), (150, 70), (160, 70), (170, 67),
     (178, 65), (178, 62), (170, 60), (162, 60), (158, 53), (150, 59),
     (142, 55), (140, 50), (135, 43), (132, 38), (127, 35), (122, 31),
     (120, 25), (115, 22), (110, 20), (108, 15), (105, 10), (103, 2),
     (100, 6), (98, 10), (95, 15), (92, 20), (89, 22), (86, 20), (80, 15),
     (77, 8), (75, 12), (72, 20), (68, 23), (62, 25), (57, 26), (52, 26),
     (50, 29), (48, 30), (44, 29), (40, 30), (36, 36), (33, 36), (30, 36),
     (27, 37), (23, 36), (22, 37), (19, 40), (16, 38), (12, 44), (8, 44),
     (3, 42), (0, 38), (-2, 37), (-6, 36)],
    # South-East Asia islands + Japan + Australia
    [(95, 5), (98, 8), (100, 2), (102, -2), (105, -5), (110, -7), (115, -8),
     (120, -10), (125, -9), (130, -4), (135, -3), (140, -8), (138, -2)],
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (140, 39),
     (141, 41), (143, 43), (145, 44), (142, 45), (140, 42)],
    [(114, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (132, -12),
     (127, -14), (122, -17), (118, -20)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)],
]


def lonlat_to_xy(lon, lat, x0, y0, w, h):
    x = x0 + (lon + 180.0) / 360.0 * w
    y = y0 + (75.0 - lat) / 130.0 * h
    return x, y


# ---------------------------------------------------------------- icons
def icon_chip(d, x, y, s, c):
    d.rectangle([x + s * .18, y + s * .18, x + s * .82, y + s * .82],
                outline=c, width=3)
    d.rectangle([x + s * .38, y + s * .38, x + s * .62, y + s * .62], fill=c)
    for i in range(3):
        t = s * (.30 + i * .20)
        d.line([(x + t, y + s * .05), (x + t, y + s * .18)], fill=c, width=2)
        d.line([(x + t, y + s * .82), (x + t, y + s * .95)], fill=c, width=2)
        d.line([(x + s * .05, y + t), (x + s * .18, y + t)], fill=c, width=2)
        d.line([(x + s * .82, y + t), (x + s * .95, y + t)], fill=c, width=2)


def icon_globe(d, x, y, s, c):
    d.ellipse([x + s * .08, y + s * .08, x + s * .92, y + s * .92],
              outline=c, width=3)
    d.ellipse([x + s * .38, y + s * .08, x + s * .62, y + s * .92],
              outline=c, width=2)
    d.line([(x + s * .08, y + s * .5), (x + s * .92, y + s * .5)], fill=c, width=2)
    d.arc([x + s * .08, y + s * .22, x + s * .92, y + s * .78], 200, 340,
          fill=c, width=2)
    d.arc([x + s * .08, y + s * .22, x + s * .92, y + s * .78], 20, 160,
          fill=c, width=2)


def icon_radar(d, x, y, s, c):
    cx, cy = x + s * .5, y + s * .55
    for r in (s * .40, s * .28, s * .16):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=2)
    d.line([(cx, cy), (cx + s * .38, cy - s * .30)], fill=c, width=3)
    d.polygon([(cx, cy - s * .42), (cx + s * .16, cy - s * .12),
               (cx - s * .05, cy - s * .10)], fill=c)


def icon_ship(d, x, y, s, c):
    d.polygon([(x + s * .10, y + s * .60), (x + s * .90, y + s * .60),
               (x + s * .78, y + s * .85), (x + s * .22, y + s * .85)], fill=c)
    d.rectangle([x + s * .44, y + s * .15, x + s * .56, y + s * .60], fill=c)
    d.polygon([(x + s * .56, y + s * .15), (x + s * .90, y + s * .45),
               (x + s * .56, y + s * .45)], fill=c)


def icon_shield(d, x, y, s, c):
    d.polygon([(x + s * .5, y + s * .08), (x + s * .88, y + s * .22),
               (x + s * .88, y + s * .55), (x + s * .5, y + s * .92),
               (x + s * .12, y + s * .55), (x + s * .12, y + s * .22)],
              outline=c, width=3)
    d.line([(x + s * .30, y + s * .50), (x + s * .45, y + s * .65),
            (x + s * .72, y + s * .35)], fill=c, width=3)


def icon_flame(d, x, y, s, c):
    d.polygon([(x + s * .50, y + s * .06), (x + s * .78, y + s * .40),
               (x + s * .88, y + s * .62), (x + s * .68, y + s * .90),
               (x + s * .32, y + s * .90), (x + s * .12, y + s * .62),
               (x + s * .24, y + s * .38)], fill=c)
    d.ellipse([x + s * .36, y + s * .55, x + s * .64, y + s * .82],
              fill=PAPER)


def icon_factory(d, x, y, s, c):
    d.rectangle([x + s * .10, y + s * .45, x + s * .90, y + s * .88], fill=c)
    d.polygon([(x + s * .10, y + s * .45), (x + s * .30, y + s * .25),
               (x + s * .50, y + s * .45), (x + s * .70, y + s * .25),
               (x + s * .90, y + s * .45)], fill=c)
    d.rectangle([x + s * .18, y + s * .12, x + s * .28, y + s * .45], fill=c)
    d.rectangle([x + s * .60, y + s * .60, x + s * .68, y + s * .72],
                fill=PAPER)
    d.rectangle([x + s * .74, y + s * .60, x + s * .82, y + s * .72],
                fill=PAPER)


def icon_scale(d, x, y, s, c):
    d.line([(x + s * .5, y + s * .12), (x + s * .5, y + s * .85)], fill=c, width=3)
    d.line([(x + s * .15, y + s * .25), (x + s * .85, y + s * .25)], fill=c, width=3)
    d.line([(x + s * .30, y + s * .85), (x + s * .70, y + s * .85)], fill=c, width=3)
    d.polygon([(x + s * .05, y + s * .45), (x + s * .25, y + s * .45),
               (x + s * .15, y + s * .62)], outline=c, width=2)
    d.polygon([(x + s * .75, y + s * .45), (x + s * .95, y + s * .45),
               (x + s * .85, y + s * .62)], outline=c, width=2)


def icon_chart(d, x, y, s, c):
    d.line([(x + s * .12, y + s * .85), (x + s * .12, y + s * .12)], fill=c, width=3)
    d.line([(x + s * .12, y + s * .85), (x + s * .90, y + s * .85)], fill=c, width=3)
    for i, h in enumerate((.30, .48, .38, .62)):
        bx = x + s * (.24 + i * .18)
        d.rectangle([bx, y + s * (.85 - h), bx + s * .12, y + s * .85], fill=c)
    d.line([(x + s * .15, y + s * .60), (x + s * .45, y + s * .38),
            (x + s * .70, y + s * .45), (x + s * .90, y + s * .20)],
           fill=RED, width=3)


def icon_ballot(d, x, y, s, c):
    d.rectangle([x + s * .12, y + s * .20, x + s * .88, y + s * .88],
                outline=c, width=3)
    d.line([(x + s * .12, y + s * .38), (x + s * .88, y + s * .38)], fill=c, width=2)
    d.line([(x + s * .28, y + s * .60), (x + s * .42, y + s * .74),
            (x + s * .68, y + s * .48)], fill=RED, width=3)


def icon_trophy(d, x, y, s, c):
    d.polygon([(x + s * .25, y + s * .12), (x + s * .75, y + s * .12),
               (x + s * .68, y + s * .55), (x + s * .32, y + s * .55)], fill=c)
    d.arc([x + s * .05, y + s * .12, x + s * .30, y + s * .45], 90, 270,
          fill=c, width=3)
    d.arc([x + s * .70, y + s * .12, x + s * .95, y + s * .45], 270, 90,
          fill=c, width=3)
    d.rectangle([x + s * .44, y + s * .55, x + s * .56, y + s * .72], fill=c)
    d.rectangle([x + s * .32, y + s * .72, x + s * .68, y + s * .82], fill=c)


def icon_chess(d, x, y, s, c):
    d.rectangle([x + s * .12, y + s * .72, x + s * .88, y + s * .88], fill=c)
    d.polygon([(x + s * .30, y + s * .72), (x + s * .38, y + s * .30),
               (x + s * .55, y + s * .18), (x + s * .52, y + s * .35),
               (x + s * .70, y + s * .28), (x + s * .62, y + s * .45),
               (x + s * .68, y + s * .72)], fill=c)
    d.ellipse([x + s * .42, y + s * .10, x + s * .58, y + s * .24], fill=c)


def icon_bat(d, x, y, s, c):
    d.line([(x + s * .20, y + s * .80), (x + s * .80, y + s * .20)], fill=c, width=4)
    d.ellipse([x + s * .55, y + s * .10, x + s * .90, y + s * .45],
              outline=c, width=3)
    d.ellipse([x + s * .12, y + s * .60, x + s * .32, y + s * .80], fill=RED)


def icon_cross(d, x, y, s, c):
    d.rectangle([x + s * .40, y + s * .10, x + s * .60, y + s * .90], fill=c)
    d.rectangle([x + s * .10, y + s * .38, x + s * .90, y + s * .58], fill=c)


def icon_deal(d, x, y, s, c):
    d.polygon([(x + s * .15, y + s * .55), (x + s * .50, y + s * .25),
               (x + s * .85, y + s * .55), (x + s * .50, y + s * .85)], fill=c)
    d.line([(x + s * .15, y + s * .55), (x + s * .85, y + s * .55)], fill=PAPER, width=2)
    d.line([(x + s * .50, y + s * .25), (x + s * .50, y + s * .85)], fill=PAPER, width=2)


ICONS = dict(chip=icon_chip, globe=icon_globe, radar=icon_radar,
             ship=icon_ship, shield=icon_shield, flame=icon_flame,
             factory=icon_factory, scale=icon_scale, chart=icon_chart,
             ballot=icon_ballot, trophy=icon_trophy, chess=icon_chess,
             bat=icon_bat, cross=icon_cross, deal=icon_deal)


def draw_icon(d, kind, x, y, s, color):
    ICONS[kind](d, x, y, s, color)


# ---------------------------------------------------------------- render
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    f_title = F(SERIF_B, 52)
    f_date = F(SANS_B, 15)
    f_strip = F(SANS_B, 13)
    f_kpi_n = F(SERIF_B, 26)
    f_kpi_l = F(SANS_B, 9)
    f_reg = F(SANS_B, 11)
    f_tl_h = F(SANS_B, 10)
    f_tl_t = F(SANS_B, 13)
    f_kick = F(SANS_B, 9)
    f_head = F(SERIF_B, 17)
    f_body = F(SANS, 11)
    f_gkick = F(SANS_B, 8)
    f_ghead = F(SERIF_B, 12)
    f_gbody = F(SANS, 9)
    f_sec = F(SANS_B, 12)
    f_also = F(SANS, 10)
    f_small = F(SANS, 9)
    f_small_b = F(SANS_B, 9)

    MX = 10
    RX = W - MX

    # ---- masthead
    d.text((MX, 8), "THE WORLD IN ONE DAY", font=f_title, fill=INK)
    icon_globe(d, RX - 58, 6, 56, INK)
    hline(d, MX, RX, 66, INK, 3)
    d.text((MX, 72), "TUESDAY, 24 NOVEMBER 2026", font=f_date, fill=RED)
    d.text((RX - d.textlength("No. 24  •  TUESDAY EDITION", font=f_date), 72),
           "No. 24  •  TUESDAY EDITION", font=f_date, fill=INK)
    hline(d, MX, RX, 92, INK, 1)
    box(d, MX, 96, W - 2 * MX, 22, fill=RED)
    strip = "36 STORIES  •  5 REGIONS  •  EVERY ONE DATED  •  TUESDAY 24 NOVEMBER 2026"
    d.text(((W - d.textlength(strip, font=f_strip)) / 2, 100), strip,
           font=f_strip, fill=(255, 255, 255))

    # ---- KPI strip
    y = 122
    kw = (W - 2 * MX - 5 * 6) // 6
    for i, (num, lab) in enumerate(KPIS):
        x = MX + i * (kw + 6)
        box(d, x, y, kw, 38, fill=NAVY)
        d.text((x + 8, y + 2), num, font=F(SERIF_B, 21), fill=(255, 255, 255))
        d.text((x + 8, y + 26), lab, font=f_kpi_l, fill=(200, 205, 220))

    # ---- region bar (colour segments) + chip legend below
    y = 164
    total = sum(c for _, c, _ in REGIONS)
    x = MX
    bar_w = W - 2 * MX
    for name, cnt, col in REGIONS:
        w = int(bar_w * cnt / total)
        box(d, x, y, w, 14, fill=col)
        x += w
    lx = MX
    ly = y + 18
    for name, cnt, col in REGIONS:
        box(d, lx, ly, 9, 9, fill=col)
        lab = "%s %d" % (name, cnt)
        d.text((lx + 12, ly - 1), lab, font=f_reg, fill=INK)
        lx += 12 + d.textlength(lab, font=f_reg) + 18
    d.text((lx, ly - 1), "—  SHARE OF TODAY'S 36 STORIES",
           font=f_reg, fill=GREY)

    # ---- timeline
    y = 194
    d.text((MX, y), "THE DAY IN UTC", font=f_sec, fill=RED)
    hline(d, MX, RX, y + 15, LINE, 1)
    ty = y + 20
    tw = (W - 2 * MX) // 6
    for i, (t, label) in enumerate(TIMELINE):
        x = MX + i * tw
        d.ellipse([x + 2, ty, x + 10, ty + 8], fill=RED)
        d.text((x, ty + 11), t, font=f_tl_t, fill=RED)
        d.text((x, ty + 26), label, font=f_tl_h, fill=INK)
    hline(d, MX, RX, 254, INK, 2)

    # ---- three lead stories
    y0 = 260
    colw = (W - 2 * MX - 2 * 10) // 3
    for i, s in enumerate(LEADS):
        x = MX + i * (colw + 10)
        d.text((x, y0), s["kicker"], font=f_kick, fill=RED)
        # illustration panel
        iy = y0 + 14
        box(d, x, iy, colw, 88, fill=(233, 226, 208), outline=LINE, width=1)
        icon_c = NAVY if i != 1 else (34, 110, 80)
        draw_icon(d, s["icon"], x + colw // 2 - 30, iy + 12, 60, icon_c)
        d.text((x + colw - 26, iy + 66), "#%d" % s["n"], font=f_kick, fill=GREY)
        hy = iy + 94
        para(d, x, hy, s["head"], f_head, colw, 19, INK, max_lines=2)
        para(d, x, hy + 40, s["body"], f_body, colw, 13, INK, max_lines=4)
        if i < 2:
            d.line([(x + colw + 5, y0), (x + colw + 5, y0 + 200)], fill=LINE, width=1)
    hline(d, MX, RX, y0 + 204, INK, 2)

    # ---- grid stories 4-15
    gy = y0 + 212
    gw = (W - 2 * MX - 3 * 8) // 4
    gh = 66
    for idx, s in enumerate(GRID):
        r, c = divmod(idx, 4)
        x = MX + c * (gw + 8)
        yy = gy + r * (gh + 6)
        box(d, x, yy, gw, gh, fill=CARD, outline=LINE, width=1)
        box(d, x, yy, 46, gh, fill=(233, 226, 208))
        draw_icon(d, s["icon"], x + 5, yy + 10, 36, NAVY)
        tx = x + 52
        d.text((tx, yy + 3), "%d  %s" % (s["n"], s["kicker"]), font=f_gkick, fill=RED)
        hy = para(d, tx, yy + 15, s["head"], f_ghead, gw - 58, 13, INK, max_lines=2)
        para(d, tx, hy + 1, s["body"], f_gbody, gw - 58, 11, GREY, max_lines=2)
    my = gy + 3 * (gh + 6) - 6

    # ---- world map
    my += 6
    d.text((MX, my), "WHERE IT HAPPENED  —  NUMBERED PINS MARK STORIES 1–15",
           font=f_sec, fill=RED)
    map_y = my + 17
    map_h = 132
    map_w = 690
    box(d, MX, map_y, map_w, map_h, fill=MAPSEA, outline=LINE, width=1)
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lo, la, MX, map_y, map_w, map_h) for lo, la in poly]
        d.polygon(pts, fill=LAND, outline=(140, 148, 128))
    pins = LEADS + GRID
    for s in pins:
        px, py = lonlat_to_xy(s["lon"], s["lat"], MX, map_y, map_w, map_h)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255), width=1)
        num = str(s["n"])
        d.text((px - d.textlength(num, font=f_small_b) / 2, py - 5),
               num, font=f_small_b, fill=(255, 255, 255))
    # pin key at right of map
    kx = MX + map_w + 10
    kw2 = RX - kx
    d.text((kx, map_y), "PIN KEY", font=f_sec, fill=INK)
    key_lines = [
        "1 Huang returns  •  USA",
        "2 COP31 collapses  •  Turkey",
        "3 NATO AWACS  •  Poland",
        "4 Warship sunk  •  Libya",
        "5 Iran blockade  •  Tehran",
        "6 Toxic blast halt  •  Iowa",
        "7 Factory fire  •  Indonesia",
        "8 EU sanctions  •  Brussels",
        "9 Market rally  •  New York",
        "10 House 258  •  Washington",
        "11 Women's WC  •  London",
        "12 Chess defence  •  Geneva",
        "13 Test drawn  •  Wellington",
        "14 AI screening  •  Oxford",
        "15 Cyber merger  •  Texas",
    ]
    yy = map_y + 17
    for ln in key_lines:
        d.text((kx, yy), ln, font=F(SANS, 8), fill=INK)
        yy += 8
    para(d, kx, yy + 1, "Every pin sits on the place the story happened.",
         F(SANS, 8), kw2, 10, GREY, max_lines=2)

    ay = map_y + map_h + 6
    d.text((MX, ay), "ALSO ON TUESDAY 24 NOVEMBER  —  21 MORE STORIES",
           font=f_sec, fill=RED)
    hline(d, MX, RX, ay + 16, INK, 1)
    ly = ay + 21
    colw2 = (W - 2 * MX - 2 * 12) // 3
    f_also = F(SANS, 9)
    for idx, (n, text) in enumerate(ALSO):
        c, r = divmod(idx, 7)
        x = MX + c * (colw2 + 12)
        yy = ly + r * 14
        d.text((x, yy), "%d." % n, font=f_small_b, fill=RED)
        d.text((x + 22, yy), text, font=f_also, fill=INK)

    by = ly + 7 * 14 + 5
    hline(d, MX, RX, by, INK, 2)
    by += 6
    # bottom row: date check (left) + certainty + sources (right)
    bw = (W - 2 * MX - 10) // 2
    box(d, MX, by, bw, 42, fill=(255, 252, 244), outline=RED, width=1)
    d.text((MX + 6, by + 3), "DATE CHECK — WHAT WAS LEFT OUT AND WHY",
           font=f_small_b, fill=RED)
    para(d, MX + 6, by + 16,
         "Alcaraz won the ATP Finals on 22 Nov, the 49ers won in Mexico City on "
         "22 Nov and Fiona the hippo died on 19 Nov — all before today.",
         f_small, bw - 12, 11, INK, max_lines=2)
    bx = MX + bw + 10
    d.text((bx, by + 3),
           "CERTAINTY:  REPORTED = confirmed  •  CLAIM = one side says so  •  "
           "FORECAST = scheduled",
           font=f_small_b, fill=INK)
    para(d, bx, by + 16,
         "Sources: Reuters, CNN, AP, BBC, Dow Jones, The Times, Times of India, "
         "France 24, Computer Weekly. First reported 22–24 Nov 2026.",
         f_small, bw - 2, 11, GREY, max_lines=2)
    # footer rule
    hline(d, MX, RX, H - 8, INK, 1)
    img.save(OUT, format="PNG", optimize=True)
    return OUT


if __name__ == "__main__":
    print(render())
