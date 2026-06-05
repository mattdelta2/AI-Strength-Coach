-- schema.sql

-- 1. Exercise Library: The global "menu" of available movements.
CREATE TABLE IF NOT EXISTS exercises (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  name TEXT NOT NULL UNIQUE,
  category TEXT NOT NULL,
  target_muscle TEXT,
  equipment TEXT NOT NULL DEFAULT 'gym'
);

-- Add equipment column to existing installs without it
ALTER TABLE exercises ADD COLUMN IF NOT EXISTS equipment TEXT NOT NULL DEFAULT 'gym';

-- 2. User Progress: Tracks current strength levels for the AI to "learn."
CREATE TABLE IF NOT EXISTS user_progress (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  exercise_name TEXT UNIQUE NOT NULL,
  current_weight FLOAT DEFAULT 20.0,
  target_reps INTEGER DEFAULT 10,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Messages: Chat persistence for cross-session memory.
CREATE TABLE IF NOT EXISTS messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,
  role TEXT,
  content TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Exercise Seed Data (54 exercises: gym + home, all categories).
--    ON CONFLICT updates equipment/muscle/category so re-running is safe.
INSERT INTO exercises (name, category, target_muscle, equipment)
VALUES
  -- ── GYM: UPPER ──────────────────────────────────────────────────────────
  ('Bench Press',              'Upper',     'Chest',         'gym'),
  ('Incline Bench Press',      'Upper',     'Chest',         'gym'),
  ('Overhead Press',           'Upper',     'Shoulders',     'gym'),
  ('Barbell Row',              'Upper',     'Back',          'gym'),
  ('Lat Pulldown',             'Upper',     'Lats',          'gym'),
  ('Cable Row',                'Upper',     'Back',          'gym'),
  ('Dumbbell Shoulder Press',  'Upper',     'Shoulders',     'gym'),
  ('Dumbbell Lateral Raise',   'Upper',     'Shoulders',     'gym'),
  ('Dumbbell Curl',            'Upper',     'Biceps',        'gym'),
  ('Barbell Curl',             'Upper',     'Biceps',        'gym'),
  ('Tricep Pushdown',          'Upper',     'Triceps',       'gym'),
  ('Skull Crushers',           'Upper',     'Triceps',       'gym'),
  ('Cable Fly',                'Upper',     'Chest',         'gym'),
  ('Chest Supported Row',      'Upper',     'Back',          'gym'),
  ('Face Pull',                'Upper',     'Rear Delts',    'gym'),

  -- ── GYM: LOWER ──────────────────────────────────────────────────────────
  ('Squat',                    'Lower',     'Quads',         'gym'),
  ('Deadlift',                 'Lower',     'Back/Legs',     'gym'),
  ('Romanian Deadlift',        'Lower',     'Hamstrings',    'gym'),
  ('Leg Press',                'Lower',     'Quads',         'gym'),
  ('Leg Curl',                 'Lower',     'Hamstrings',    'gym'),
  ('Leg Extension',            'Lower',     'Quads',         'gym'),
  ('Hip Thrust',               'Lower',     'Glutes',        'gym'),
  ('Calf Raise',               'Lower',     'Calves',        'gym'),
  ('Hack Squat',               'Lower',     'Quads',         'gym'),
  ('Walking Lunge',            'Lower',     'Quads/Glutes',  'gym'),

  -- ── GYM: FULL BODY ──────────────────────────────────────────────────────
  ('Power Clean',              'Full Body', 'Full Body',     'gym'),
  ('Barbell Complex',          'Full Body', 'Full Body',     'gym'),
  ('Farmers Carry',            'Full Body', 'Full Body',     'gym'),

  -- ── GYM: CORE ───────────────────────────────────────────────────────────
  ('Cable Crunch',             'Core',      'Abs',           'gym'),
  ('Ab Wheel Rollout',         'Core',      'Abs',           'gym'),

  -- ── HOME: UPPER ─────────────────────────────────────────────────────────
  ('Push-Up',                  'Upper',     'Chest',         'home'),
  ('Wide Push-Up',             'Upper',     'Chest',         'home'),
  ('Diamond Push-Up',          'Upper',     'Triceps',       'home'),
  ('Pike Push-Up',             'Upper',     'Shoulders',     'home'),
  ('Pull-Up',                  'Upper',     'Lats',          'home'),
  ('Chin-Up',                  'Upper',     'Biceps',        'home'),
  ('Inverted Row',             'Upper',     'Back',          'home'),
  ('Tricep Dip',               'Upper',     'Triceps',       'home'),

  -- ── HOME: LOWER ─────────────────────────────────────────────────────────
  ('Bodyweight Squat',         'Lower',     'Quads',         'home'),
  ('Bulgarian Split Squat',    'Lower',     'Quads/Glutes',  'home'),
  ('Reverse Lunge',            'Lower',     'Quads/Glutes',  'home'),
  ('Glute Bridge',             'Lower',     'Glutes',        'home'),
  ('Single-Leg Glute Bridge',  'Lower',     'Glutes',        'home'),
  ('Nordic Hamstring Curl',    'Lower',     'Hamstrings',    'home'),
  ('Step-Up',                  'Lower',     'Quads',         'home'),
  ('Wall Sit',                 'Lower',     'Quads',         'home'),

  -- ── HOME: FULL BODY ─────────────────────────────────────────────────────
  ('Burpee',                   'Full Body', 'Full Body',     'home'),
  ('Mountain Climber',         'Full Body', 'Full Body',     'home'),
  ('Bear Crawl',               'Full Body', 'Full Body',     'home'),

  -- ── HOME: CORE ──────────────────────────────────────────────────────────
  ('Plank',                    'Core',      'Abs',           'home'),
  ('Side Plank',               'Core',      'Obliques',      'home'),
  ('Hollow Body Hold',         'Core',      'Abs',           'home'),
  ('Dead Bug',                 'Core',      'Abs',           'home'),
  ('Bicycle Crunch',           'Core',      'Obliques',      'home'),
  ('Leg Raise',                'Core',      'Abs',           'home')
ON CONFLICT (name) DO UPDATE SET
  equipment     = EXCLUDED.equipment,
  target_muscle = EXCLUDED.target_muscle,
  category      = EXCLUDED.category;
