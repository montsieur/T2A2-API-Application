from flask import Blueprint
from datetime import date
import click
from init import db, bcrypt
from sqlalchemy.exc import IntegrityError, OperationalError, DatabaseError

from models.user import User
from models.card import Card
from models.set import Set
from models.condition import Condition
from models.rarity import Rarity
from models.wishlist import Wishlist
from models.user_card import UserCard
from models.status import Status
from models.trading import Trade

cli_blueprint = Blueprint('db', __name__)

# Command to create all tables in database
@cli_blueprint.cli.command('create_db')
def create_db():
    try:
        db.drop_all()
        db.create_all()
        print('Tables created successfully.')
    except OperationalError as e:
        print(f"Operational error occurred while creating tables: {str(e)}")
    except DatabaseError as e:
        print(f"Database error occurred while creating tables: {str(e)}")

# Command to drop all tables in database
@cli_blueprint.cli.command('drop_db')
def drop_db():
    try:
        db.drop_all()
        print('Tables dropped successfully.')
    except OperationalError as e:
        print(f"Operational error occurred while dropping tables: {str(e)}")
    except DatabaseError as e:
        print(f"Database error occurred while dropping tables: {str(e)}")

# Seed the database with initial/sample data
@cli_blueprint.cli.command('seed_db')
def seed_db():
    try:
        # Seed Sets
        sets = [
            Set(
                set_name='Base Set',
                release_date=date(1999, 1, 9)
            ),
            Set(
                set_name='Jungle',
                release_date=date(1999, 6, 16)
            ),
            Set(
                set_name='Fossil',
                release_date=date(1999, 10, 10)
            )
        ]
        db.session.query(Set).delete()
        db.session.add_all(sets)
        db.session.commit()

        # Seed Rarities
        rarities = [
            Rarity(rarity_name='Common'),
            Rarity(rarity_name='Uncommon'),
            Rarity(rarity_name='Rare'),
            Rarity(rarity_name='Holographic Rare'),

        ]
        db.session.query(Rarity).delete()
        db.session.add_all(rarities)
        db.session.commit()

        # Seed Conditions
        conditions = [
            Condition(condition_name='Mint'),
            Condition(condition_name='Near Mint'),
            Condition(condition_name='Good'),
            Condition(condition_name='Fair'),
            Condition(condition_name='Poor')
        ]
        db.session.query(Condition).delete()
        db.session.add_all(conditions)
        db.session.commit()

        # Retrieve sets and rarities from the database
        sets = Set.query.all()
        rarities = Rarity.query.all()

        # Seed Cards
        cards = [
            Card(name='Charizard', card_type='Fire', rarity_id=rarities[3].id, set_id=sets[0].id),
            Card(name='Pikachu', card_type='Electric', rarity_id=rarities[0].id, set_id=sets[1].id),
            Card(name='Snorlax', card_type='Normal', rarity_id=rarities[2].id, set_id=sets[2].id),
            Card(name='Bulbasaur', card_type='Grass', rarity_id=rarities[0].id, set_id=sets[0].id),
            Card(name='Mewtwo', card_type='Psychic', rarity_id=rarities[3].id, set_id=sets[1].id)
        ]
        
        db.session.query(Card).delete()
        db.session.add_all(cards)
        db.session.commit()

        # Seed Users
        users = [
            User(
                username='AshKetchum',
                email='ash@pallet.com',
                password_hash=bcrypt.generate_password_hash('pikachu').decode('utf-8'),
                is_admin=True
            ),
            User(
                username='MistyWater',
                email='misty@cerulean.com',
                password_hash=bcrypt.generate_password_hash('starmie').decode('utf-8')
            ),
            User(
                username='BrockRock',
                email='brock@pewter.com',
                password_hash=bcrypt.generate_password_hash('geodude').decode('utf-8')
            )
        ]
        db.session.query(User).delete()
        db.session.add_all(users)
        db.session.commit()

        # Retrieve users and cards after committing to get their IDs
        users = User.query.all()
        cards = Card.query.all()

        # Seed Wishlist Entries
        wishlists = [
            Wishlist(user_id=users[0].id, card_id=cards[1].id),
            Wishlist(user_id=users[1].id, card_id=cards[0].id),
            Wishlist(user_id=users[2].id, card_id=cards[3].id)
        ]
        db.session.query(Wishlist).delete()
        db.session.add_all(wishlists)
        db.session.commit()

        print('Tables seeded successfully.')

        # Seed UserCards
        user_cards = [
            UserCard(user_id=users[0].id, card_id=cards[0].id, condition_id=conditions[0].id),
            UserCard(user_id=users[1].id, card_id=cards[1].id, condition_id=conditions[1].id),
            UserCard(user_id=users[2].id, card_id=cards[2].id, condition_id=conditions[2].id)
        ]
        db.session.query(UserCard).delete()
        db.session.add_all(user_cards)
        db.session.commit()

        print('Tables seeded successfully.')

        # Seed Statuses
        statuses = [
            Status(status_name='Pending'),
            Status(status_name='Accepted'),
            Status(status_name='Declined'),
            Status(status_name='Cancelled')
        ]
        db.session.query(Status).delete()
        db.session.add_all(statuses)
        db.session.commit()

        print('Statuses seeded successfully.')

        # Seed Trades
        trades = [
            Trade(
                offering_user_id=users[0].id,
                receiving_user_id=users[1].id,
                offering_card_id=cards[0].id,
                receiving_card_id=cards[1].id,
                offering_quantity=1,
                receiving_quantity=1,
                status_id=statuses[0].id  # Pending
            ),
            Trade(
                offering_user_id=users[1].id,
                receiving_user_id=users[0].id,
                offering_card_id=cards[1].id,
                receiving_card_id=cards[0].id,
                offering_quantity=2,
                receiving_quantity=1,
                status_id=statuses[1].id  # Accepted
            )
        ]
        db.session.query(Trade).delete()
        db.session.add_all(trades)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        print(f"Error seeding the database: {e}")

# Command to add a new set
@cli_blueprint.cli.command('add_set')
@click.argument("name")
@click.argument("release_date")
def add_set(name, release_date):
    try:
        release_date_obj = date.fromisoformat(release_date) # Convert ISO date string to date object

        new_set = Set(set_name=name, release_date=release_date_obj) # Convert date object to datetime object
        db.session.add(new_set) #
        db.session.commit()

        print(f"Set '{name}' added successfully with release date {release_date}.")

    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
    except Exception as e:
        db.session.rollback()
        print(f"Error adding set: {e}")

# Command to add a new card
@cli_blueprint.cli.command('add_card')
@click.argument("name")
@click.argument("card_type")
@click.argument("rarity_id", type=int)
@click.argument("set_id", type=int)
def add_card(name, card_type, rarity_id, set_id):
    try:
        rarity = Rarity.query.get(rarity_id)
        card_set = Set.query.get(set_id)

        if not rarity or not card_set:
            print("Rarity ID or Set ID not found.")
            return

        new_card = Card(name=name, card_type=card_type, rarityID=rarity_id, setID=set_id)
        db.session.add(new_card)
        db.session.commit()

        print(f"Card '{name}' added successfully.")

    except IntegrityError:
        db.session.rollback()
        print("An integrity error occurred while seeding the database. Check for unique constraints.")
    except OperationalError as e:
        db.session.rollback()
        print(f"Operational error occurred while seeding the database: {str(e)}")
    except DatabaseError as e:
        db.session.rollback()
        print(f"Database error occurred while seeding the database: {str(e)}")

# Command to add a new rarity
@cli_blueprint.cli.command('add_rarity')
@click.argument("rarity_name")
def add_rarity(rarity_name):
    try:
        new_rarity = Rarity(rarity_name=rarity_name)
        db.session.add(new_rarity)
        db.session.commit()

        print(f"Rarity '{rarity_name}' added successfully.")

    except Exception as e:
        db.session.rollback()
        print(f"Error adding rarity: {e}")
        
# Command to add a new user
@cli_blueprint.cli.command('create_user')
@click.argument("username", default="user")
@click.argument("email", default="user@localhost")
@click.argument("password", default="user")
@click.option("--admin", is_flag=True)
def create_user(username, email, password, admin):
    try:
        hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=hash_password, is_admin=admin)
        db.session.add(user)
        db.session.commit()
        print(f"User '{username}' created successfully.")
    except IntegrityError:
        db.session.rollback()
        print(f"Error: Email or username '{email}' is already registered.")
    except OperationalError as e:
        db.session.rollback()
        print(f"Operational error occurred while creating user: {str(e)}")
    except DatabaseError as e:
        db.session.rollback()
        print(f"Database error occurred while creating user: {str(e)}")

# Command to delete a user
@cli_blueprint.cli.command('delete_user')
@click.argument("username")
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        print(f"User '{username}' does not exist.")
        return

    db.session.delete(user)
    try:
        db.session.commit()
        print(f"User '{username}' deleted successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {e}")

