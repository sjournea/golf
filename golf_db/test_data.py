import datetime

canyon_lakes_mens_holes = [
  {'par': 4, 'handicap': 17},
  {'par': 5, 'handicap':  9},
  {'par': 3, 'handicap':  5},
  {'par': 4, 'handicap': 11},
  {'par': 3, 'handicap': 15},
  {'par': 4, 'handicap': 13},
  {'par': 5, 'handicap':  7},
  {'par': 4, 'handicap':  1},
  {'par': 4, 'handicap':  3},

  {'par': 3, 'handicap':  8},
  {'par': 4, 'handicap': 14},
  {'par': 4, 'handicap': 12},
  {'par': 3, 'handicap': 16},
  {'par': 5, 'handicap':  4},
  {'par': 3, 'handicap': 10},
  {'par': 4, 'handicap': 18},
  {'par': 5, 'handicap':  2},
  {'par': 4, 'handicap':  6},
]
sj_muni_holes = [
  {'par': 5, 'handicap': 15},
  {'par': 4, 'handicap':  1},
  {'par': 4, 'handicap':  5},
  {'par': 3, 'handicap': 17},
  {'par': 4, 'handicap': 11},
  {'par': 4, 'handicap':  7},
  {'par': 3, 'handicap':  9},
  {'par': 4, 'handicap':  3},
  {'par': 5, 'handicap': 13},

  {'par': 4, 'handicap': 12},
  {'par': 5, 'handicap':  4},
  {'par': 3, 'handicap': 18},
  {'par': 4, 'handicap':  6},
  {'par': 4, 'handicap': 16},
  {'par': 4, 'handicap':  2},
  {'par': 4, 'handicap':  8},
  {'par': 3, 'handicap': 10},
  {'par': 5, 'handicap': 14},
]    
diablo_grande_men_holes = [
  {'par': 4, 'handicap': 15},
  {'par': 4, 'handicap':  9},
  {'par': 4, 'handicap':  3},
  {'par': 3, 'handicap': 11},
  {'par': 5, 'handicap':  7},
  {'par': 4, 'handicap': 13},
  {'par': 3, 'handicap':  5},
  {'par': 4, 'handicap':  1},
  {'par': 5, 'handicap': 17},

  {'par': 4, 'handicap':  8},
  {'par': 3, 'handicap': 14},
  {'par': 5, 'handicap':  4},
  {'par': 4, 'handicap': 16},
  {'par': 4, 'handicap':  2},
  {'par': 4, 'handicap':  6},
  {'par': 5, 'handicap': 12},
  {'par': 3, 'handicap': 18},
  {'par': 4, 'handicap': 10},
]    
poppy_hills_men_holes = [
  {'par': 4, 'handicap':  7},
  {'par': 3, 'handicap': 15},
  {'par': 4, 'handicap':  9},
  {'par': 5, 'handicap':  3},
  {'par': 4, 'handicap':  1},
  {'par': 3, 'handicap': 17},
  {'par': 4, 'handicap': 13},
  {'par': 4, 'handicap': 11},
  {'par': 5, 'handicap':  5},

  {'par': 5, 'handicap':  8},
  {'par': 3, 'handicap': 18},
  {'par': 4, 'handicap':  4},
  {'par': 4, 'handicap': 10},
  {'par': 4, 'handicap': 12},
  {'par': 3, 'handicap': 14},
  {'par': 4, 'handicap':  2},
  {'par': 3, 'handicap': 16},
  {'par': 5, 'handicap':  6},
]

GolfCourseTestData = [
  {'name': 'Canyon Lakes',    'holes': canyon_lakes_mens_holes},
  {'name': 'Santa Jose Muni', 'holes': sj_muni_holes},
  {'name': 'Diablo Grande',   'holes': diablo_grande_men_holes},
  {'name': 'Poppy Hills',     'holes': poppy_hills_men_holes},
]

GolfPlayerTestData = [
  {'first_name': 'Steve', 'last_name': 'Journeay', 'nick_name': 'Hammy',  'handicap': 20.4},
  {'first_name': 'Chris', 'last_name': 'Jensen',   'nick_name': 'Snake',  'handicap': 17.9},
  {'first_name': 'Rob',   'last_name': 'Sullivan', 'nick_name': 'Spanky', 'handicap': 17.9},
  {'first_name': 'Mike',  'last_name': 'Davis',    'nick_name': 'Rock',   'handicap': 22.0},
]

GolfRoundTestData = [
  { 'date': datetime.datetime(2017, 3, 7), 
    'course': GolfCourseTestData[0],
    'players': GolfPlayerTestData,
  },
]