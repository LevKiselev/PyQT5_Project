# ������ �� PyQT �����������

��������� �������� � ������ �������� ����� ������ ����� � ���������� ��� �����������:
1. ������ �����
2. ������ ��������
3. ��� �����
������� ���� �������� ������ ��������. �� ������ (���������) �������� ������������ �����
������ ���� ��� ��� ���������� � ���� ������ ����������� ���, � ����� ������� ����.
� ������ ���� ������� ������� ����� � �������. ��� ������ ���� ������������� �����������
������, ��������� ������ � ���������� (� ����������� �� ��������).


## ���������� ������


### ������������

readme.md - ���� ����
requirements.txt - ������ ������������ ������� �������, ��������� � ������� pip freeze


### �����, ����������� ��� ������� � ������ ���������

main.py - ������� ���������
numbers_game.py - ������ � ��������� ������ ���� "������ �����"
picture_game.py - ������ � ��������� ����c�� ��� "����� ��������" � "��� �����"
rules.py - ������ � ��������� ����c�� �������������� ����

������ ������������ ����������, ��������������� �� ui-������ � ������� PyUIC:

main_ui.py - ������� ���� ���������
numbers_ui.py - ������ ���� "������ �����"
picture_ui.py - ������ ��� "������ ��������" � "��� �����"
rules_ui.py - ���� ������ ����
info_ui.py - �������������� ����
start_ui.py - ������ ��������� �������
userlist_ui.py - ���� ������ ������� � ����������

������ ��������, ��������������� �� qrc-������ � ����������� � ������� Pyrcc5

start_rc.py - ������ ������ ��������� ������� (�������� ������ �� ����)
pics_rc.py - ������� ����������� ��� ��� (����� ���)

records.db - ���� ������ �� ������� ������� � ����������� ���.
� ������ �� ���������� ��������� ������� ����� ������ ����.


### ����������� ����

� �������� dist ����� ��������� � ������� pyinstaller ����������� ���� **puzzles.exe**
��������� ������ � Windows 8/10


### �������������� �����

� �������� src ����� ui- � qrc-����� ��� QtDesigner, � ����� �������� ������ � �������������.
��� ������ ��������� ��� �� �����, �.�. ��� ������������� � py-������.


## ������ � ������ ���������

��� ������ ��������� ���������� �������� ���������� ������ ������ PyQT5.
��������� ������, ������������ � ���������, �������� ����������� � ��������� �� �������:
sys, sqlite3, datetime, random.

��������� ����� main.py, ��� ���� ��������� 12 ����������������� py-������ ������ ������ � ���
� ����� ��������. � ������ ������ ��������... �� ������ ������, � ���� �������� :)
�������� ����� �����! :)
