class BaseCharacter:

    def __init__(self, name, health, block_mult):
        self.class_name = name
        self.health = health
        self.block_reduction = block_mult
        self.max_health = health
        self.is_blocking = False

    def take_damage(self, damage):
        if self.is_blocking:
            original_damage = damage
            damage *= self.block_reduction
            blocked_damage = original_damage - damage
            self.is_blocking = False
            if self.health > damage:
                self.health -= damage
                return f"{self.class_name} has blocked {blocked_damage} damage, {damage} damage taken"
            
            else:
                self.health = 0
                return f"{self.class_name} has been defeated"


        if self.health > damage:
            self.health -= damage
            return f"{self.class_name} has taken {damage} damage"

        else:
            self.health = 0
            return f"{self.class_name} has been defeated"


    def block(self):
        self.is_blocking = True
        return f"{self.class_name} is blocking"


    def deal_damage(self, damage, target):
        message = target.take_damage(damage)
        return message


    def heal(self, amount):
        if self.health + amount > self.max_health:
            self.health = self.max_health
            return f"{self.class_name} has been healed to max health"

        else:
            self.health += amount
            return f"{self.class_name} has healed {amount} health"



class Warrior(BaseCharacter):

    def __init__(self):
        super().__init__("Warrior", 350, 0.5)

        self.moveset = {
            "Slash": 50, 
            "Heavy Slash": 100,
            "Block": 0,
            "Heal": 15,
        }

        


class Tank(BaseCharacter):

    def __init__(self):
        super().__init__("Tank", 500, 0.2)

        self.moveset = {
            "Slash": 20, 
            "Shield Bash": 40,
            "Block": 0,
            "Heal": 30
         }



class Mage(BaseCharacter):

    def __init__(self):
        super().__init__("Mage", 200, 0.8)
        
        self.moveset = {
            "Fireball": 100, 
            "Lightning": 150,
             "Block": 0,
             "Heal": 50
        }

        
