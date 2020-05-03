# makefile for grid-baseball
#
APPS = sqlmain.py
SUB_DIRS = util golf_db golf_db/data test views
# python black for code formatting
BLACK := black
BLACK_OPTS := -v
FLAKE := flake8
FLAKE_OPTS :=  --ignore=E501,W503
# pylint
LINT := pylint
LINT_OPTS :=

#TARGETS := lint black flake
TARGETS := black

all: black

black: $(APPS) $(SUB_DIRS) 
	$(BLACK) $(BLACK_OPTS) $^

flake: $(APPS) $(SUB_DIRS) 
	$(FLAKE) $(FLAKE_OPTS) $^

lint: $(APPS) 
	$(LINT) $(LINT_OPTS) $^



