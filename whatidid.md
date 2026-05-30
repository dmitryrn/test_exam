- added pytest conf because it was needed to make make test work
- moved mutmut conf to setup.cfg, because that's per docs and makes it work
- realized that python 3.14 is too new mutmut doens't work with it, downgraded to 3.12

# mut
## orig
⠋ 107/107  🎉 0  ⏰ 0  🤔 0  🙁 107  🔇 0
107 mutants

# cov
## orig
│((.venv) ) ➜  mutation_project git:(master) ✗ coverage report -m                                                                                             │
│Name                    Stmts   Miss  Cover   Missing                                                                                                        │
│-----------------------------------------------------                                                                                                        │
│billing/__init__.py         7      0   100%                                                                                                                  │
│billing/calculator.py      79     46    42%   32, 37-38, 42-44, 48, 52-54, 58, 62-68, 72-75, 79, 83-85, 89-93, 97-100, 104-105, 109, 113-114, 118, 122-123, 1│
│27, 131, 135                                                                                                                                                 │
│-----------------------------------------------------                                                                                                        │
│TOTAL                      86     46    47%                                                                                                                  │
