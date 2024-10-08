from init import db, ma
from marshmallow import fields, validates, ValidationError
from marshmallow.validate import Regexp
from flask_bcrypt import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    user_cards = db.relationship("UserCard", back_populates="user")
    trades_offered = db.relationship('Trade', foreign_keys='Trade.offering_user_id', back_populates='offering_user')
    trades_received = db.relationship('Trade', foreign_keys='Trade.receiving_user_id', back_populates='receiving_user')
    wishlists = db.relationship("Wishlist", back_populates="user")

    def __repr__(self):
        return f'<User {self.username}>'
    
    # Password hashing
    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8')

    # Password verification
    def check_password(self, password): 
        return check_password_hash(self.password_hash, password)

    
class UserSchema(ma.Schema):
    # Define how to serialize/deserialize user objects
    id = fields.Int()
    username = fields.Str(required=True)
    email = fields.String(required=True, validate=Regexp(r"^\S+@\S+\.\S+$", error="Invalid Email Format."))
    is_admin = fields.Bool()
    user_cards = fields.List(fields.Nested('UserCardSchema', only=("id", "card_id", "condition_id")))
    trades_offered = fields.List(fields.Nested('TradingSchema', only=("id", "receiving_user_id", "status")))
    trades_received = fields.List(fields.Nested('TradingSchema', only=("id", "offering_user_id", "status")))
    wishlists = fields.List(fields.Nested('WishlistSchema', only=("id", "card_id")))

    @validates('username')
    def validate_name(self, name):
        if not name:
            raise ValidationError("Username cannot be empty.")
        if len(name) < 2:
            raise ValidationError("Username must be at least 2 characters long.")

    class Meta:
        fields = (
            "id", "username", "email", "is_admin", "user_cards", "trades_offered", "trades_received", "wishlists"
        )

# To handle a single user object
user_schema = UserSchema()

# To handle a list of user objects
users_schema = UserSchema(many=True)


# To handle a single user object
user_schema = UserSchema()

# To handle a list of user objects
users_schema = UserSchema(many=True)
