import sqlite3
from random import randint

print('***************************************************************************************************************')
print('*                                    Welcome to the Banking App                                               *')
print('*                                                                                                             *')
print('*                                 - Create / Delete account                                                   *')
print('*                                 - Manage your account                                                       *')
print('*                                 - Transfer funds and much more !                                            *')
print('*                                                                                                             *')
print('***************************************************************************************************************')

conn = sqlite3.connect('bankyStuff.sqlite')

cur = conn.cursor()

cur.execute('DROP Table account')

cur.execute('Create table if not exists account(id integer, number text, pin text, balance integer default 0);')

cur.execute('DROP Table transactions')

cur.execute('Create table if not exists transactions(id integer,amount integer, action text);')

conn.commit()


class BankingSystem:
    id = 0

    def __init__(self):
        self.cardNumber = ''
        self.cardPin = 0000

    def luhn_algorithm(self, number, p):
        checksum = 0
        for k in range(len(number)):
            n = int(number[k]) % 10
            if (k+1) % 2 != 0:
                n *= 2
            if n > 9:
                n -= 9
            checksum += n
        if p == 1:
            if checksum % 10 == 0:
                return True
            return False
        else:
            if checksum % 10 == 0:
                self.cardNumber += '0'
            else:
                self.cardNumber += str(abs((checksum % 10)-10))
            return self.cardNumber

    def card_number(self):
        self.cardNumber = '400000'
        acc_num = randint(100000000, 999999999)
        self.cardNumber += str(acc_num)
        self.luhn_algorithm(self.cardNumber, 0)
        return self.cardNumber

    def create_account(self):
        print('Your card has been created')
        self.card_number()
        self.cardPin = randint(1000, 9999)
        cur.execute(f'insert into account values ({self.id+1}, {self.cardNumber}, {self.cardPin}, {0.0});')
        conn.commit()
        print(f'Your card number is : \n{self.cardNumber}')
        print(f'Your pin is : \n{self.cardPin}')
        print()

    def login(self):
        print('Enter card number: ')
        num = input('> ')
        print('Enter your PIN: ')
        pin = int(input('> '))
        cur.execute(f'SELECT * from account where number == {num} AND pin == {pin};')
        try:
            user = cur.fetchone()
            cnum, cpin = user[1], user[2]
            if num == cnum and pin == int(cpin):
                print('\nYou have successfully logged in!')
                self.logged_in(cnum)
            else:
                print('\nWrong card number or PIN!')
        except TypeError:
            print('\nWrong card number or PIN!')
        print()

    def logged_in(self, key):
        flag = True
        while flag:
            print()
            print('1. Balance\n2. Add income\n3. Do transfer\n4. Change pin\n5. Recent Transactions\n6. Close account\n7. Log out')
            inp = input('> ')
            print()
            bal = self.manage_bal(key)
            if inp == '1':
                print(f'Your balance is {bal}')
            elif inp == '2':
                self.credit(key, bal)
            elif inp == '3':
                self.make_transfer(key, bal)
            elif inp == '4':
                self.change_pin(key)
            elif inp == '5':
                self.recent_transactions(key)
            elif inp == '6':
                self.del_account(key)
                print('Your account was deleted !!')
                flag = False
            elif inp == '7':
                print('\nYou have successfully logged out!')
                flag = False

    @staticmethod
    def manage_bal(c_num):
        cur.execute(f'SELECT balance from account where number == {c_num};')
        return float(cur.fetchone()[0])

    @staticmethod
    def credit(c, bal):
        print('Enter amount to be credited: ')
        amt = float(input('> '))
        cur.execute(f'UPDATE account set balance = {bal+amt} where number == {c};')
        print(f'\n{amt} credited successfully !')
        cur.execute(f'INSERT INTO transactions values({c[6:15]}, {amt}, "credited");')
        conn.commit()

    def make_transfer(self, acc, bal):
        print('Enter the receiver\'s card number: ')
        c = input('> ')
        if c != acc:
            fort = self.luhn_algorithm(c, 1)
            if fort:
                cur.execute(f'SELECT EXISTS(SELECT number from account where number == {c});')
                if cur.fetchone()[0] == 1:
                    print('Enter amount to be credited: ')
                    amt = float(input('> '))
                    if amt <= bal:
                        cur.execute(f'UPDATE account set balance = {bal-amt} where number == {acc};')
                        cur.execute(f'SELECT balance from account where number  == {c};')
                        u_bal = cur.fetchone()[0]
                        cur.execute(f'UPDATE account set balance = {u_bal+amt} where number == {c};')
                        print(f'\n{amt} transferred successfully !')
                        cur.execute(f'INSERT INTO transactions values({acc[6:15]}, {amt}, "debited");')
                        cur.execute(f'INSERT INTO transactions values({c[6:15]}, {amt}, "credited");')
                        conn.commit()
                    else:
                        print('\nNot enough money!')
                else:
                    print('\nSuch a card does not exist.')
            else:
                print("\nProbably you made a mistake in the card number. Please try again!")
        else:
            print("\nYou can't transfer money to the same account!")

    @staticmethod
    def del_account(acc):
        cur.execute(f'delete from account where number == {acc};')
        conn.commit()

    def change_pin(self, c_num):
        print('Enter new pin: ')
        n_pin = input('> ')
        if len(n_pin) == 4:
            cur.execute(f'UPDATE account SET pin == {n_pin} where number == {c_num};')
            conn.commit()
            print('Your pin was changed successfully ! \n')
        else:
            self.change_pin(c_num)

    @staticmethod
    def recent_transactions(key):
        accnum = key[6:15]
        cur.execute(f'SELECT * from transactions where id == {accnum};')
        transactions = cur.fetchall()
        if len(transactions) > 0:
            print('***************')
            print('Amount\tAction')
            for transac in transactions:
                print(f'{transac[1]}\t\t{transac[2]}')
            print('***************')
        else:
            print('No recent transactions')


bankingRecord = BankingSystem()

while True:
    print()
    print("""1. Create an account\n2. Log into account\n0. Exit""")
    val = input('> ')
    print()
    if val == '1':
        bankingRecord.create_account()
    elif val == '2':
        bankingRecord.login()
    else:
        exit(0)
