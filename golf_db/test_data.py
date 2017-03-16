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

sj_muni_tees = [
  {'gender': 'mens', 'name': 'Gold',     'rating': 71.9, 'slope': 123 },
  {'gender': 'mens', 'name': 'Black',    'rating': 70.1, 'slope': 118 },
  {'gender': 'mens', 'name': 'Silver',   'rating': 65.5, 'slope': 109 },
  {'gender': 'womens', 'name': 'Black',  'rating': 75.6, 'slope': 125 },
  {'gender': 'womens', 'name': 'Silver', 'rating': 71.5, 'slope': 116 },
  {'gender': 'womens', 'name': 'Orange', 'rating': 63.4, 'slope': 103 },
]

canyon_lake_tees = [
  {'gender': 'mens', 'name': 'Blue',  'rating': 71.9, 'slope': 133 },
  {'gender': 'mens', 'name': 'White', 'rating': 69.7, 'slope': 131 },
  {'gender': 'womens', 'name': 'White', 'rating': 74.8, 'slope': 134 },
  {'gender': 'womens', 'name':'Green',  'rating': 70.5, 'slope': 124 },
]

diablo_grande_tees = [
  {'gender': 'mens', 'name': 'Black',  'rating': 75.4, 'slope': 138 },
  {'gender': 'mens', 'name': 'Blue',  'rating': 74.1, 'slope': 135 },
  {'gender': 'mens', 'name': 'White', 'rating': 71.6, 'slope': 129 },
]

poppy_hills_tees = [
  {'gender': 'mens', 'name': 'Jones', 'rating': 73.5, 'slope': 135 },
  {'gender': 'mens', 'name': 'pppp',  'rating': 72.1, 'slope': 132 },
  {'gender': 'mens', 'name': 'ppp',   'rating': 70.5, 'slope': 126 },
  {'gender': 'mens', 'name': 'pp',    'rating': 68.2, 'slope': 121 },
  {'gender': 'mens', 'name': 'p',     'rating': 65.6, 'slope': 116 },
]

GolfCourseTestData = [
  {'name': 'Canyon Lakes',    'holes': canyon_lakes_mens_holes, 'tees': canyon_lake_tees},
  {'name': 'Santa Jose Muni', 'holes': sj_muni_holes, 'tees': sj_muni_tees},
  {'name': 'Diablo Grande',   'holes': diablo_grande_men_holes, 'tees':diablo_grande_tees},
  {'name': 'Poppy Hills',     'holes': poppy_hills_men_holes, 'tees':poppy_hills_tees},
]

GolfPlayerTestData = [
  {'first_name': 'Steve', 'last_name': 'Journeay', 'nick_name': 'Hammy',  'handicap': 20.4},
  {'first_name': 'Chris', 'last_name': 'Jensen',   'nick_name': 'Snake',  'handicap': 17.9},
  {'first_name': 'Rob',   'last_name': 'Sullivan', 'nick_name': 'Spanky', 'handicap': 17.9},
  {'first_name': 'Mike',  'last_name': 'Davis',    'nick_name': 'Rock',   'handicap': 22.0},
]

GolfScoreTestData = [
  {'player': GolfPlayerTestData[0], 'gross': [4,8,6,8,4,5,6,7,9, 6,6,6,6,6,6,6,6,6]},
  {'player': GolfPlayerTestData[1], 'gross': [5,5,5,5,5,5,5,5,5, 5,5,5,5,5,5,5,5,5]},
  {'player': GolfPlayerTestData[2], 'gross': [7,7,7,7,7,7,7,7,7, 7,7,7,7,7,7,7,7,7]},
  {'player': GolfPlayerTestData[3], 'gross': [8,8,8,8,8,8,8,8,8, 8,8,8,8,8,8,8,8,8]},
]

GolfRoundTestData = [
  { 'date': datetime.datetime(2017, 3, 7), 
    'course': GolfCourseTestData[0],
    'players': GolfScoreTestData,
  },
]