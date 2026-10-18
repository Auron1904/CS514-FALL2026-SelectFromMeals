USE select_from_meals;

DROP VIEW IF EXISTS daily_totals;
DROP VIEW IF EXISTS meal_totals;

-- One row per meal, with its nutrition totals.
CREATE VIEW meal_totals AS
SELECT m.meal_id,
       m.user_id,
       m.meal_date,
       m.meal_type,
       COUNT(*) AS item_count,
       SUM(f.calories_per_100g * mi.quantity_g / 100) AS calories,
       SUM(f.protein_g * mi.quantity_g / 100) AS protein_g,
       SUM(f.carbs_g * mi.quantity_g / 100) AS carbs_g,
       SUM(f.fat_g * mi.quantity_g / 100) AS fat_g
FROM meals m
JOIN meal_items mi ON mi.meal_id = m.meal_id
JOIN foods f ON f.food_id = mi.food_id
GROUP BY m.meal_id, m.user_id, m.meal_date, m.meal_type;

-- One row per user per day, built on top of meal_totals.
CREATE VIEW daily_totals AS
SELECT user_id,
       meal_date,
       COUNT(*) AS meals,
       SUM(calories) AS calories,
       SUM(protein_g) AS protein_g,
       SUM(carbs_g) AS carbs_g,
       SUM(fat_g) AS fat_g
FROM meal_totals
GROUP BY user_id, meal_date;