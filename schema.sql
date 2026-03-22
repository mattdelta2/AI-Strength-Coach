-- 1. Exercise Library: The global "menu" of available movements.
CREATE TABLE IF NOT EXISTS exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL, -- e.g., 'Upper', 'Lower', 'Full Body'
    target_muscle TEXT
);

-- 2. User Progress: Tracks current strength levels for the AI to "learn."
CREATE TABLE IF NOT EXISTS user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exercise_name TEXT UNIQUE NOT NULL,
    current_weight FLOAT DEFAULT 20.0,
    target_reps INTEGER DEFAULT 10,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Initial Seed Data: Basic exercises to get the Agent started.
INSERT INTO exercises (name, category, target_muscle) 
VALUES 
    ('Bench Press', 'Upper', 'Chest'),
    ('Squat', 'Lower', 'Quads'),
    ('Deadlift', 'Lower', 'Back/Legs'),
    ('Overhead Press', 'Upper', 'Shoulders'),
    ('Bicep Curls', 'Upper', 'Biceps'),
    ('Tricep Pushdowns', 'Upper', 'Triceps')
ON CONFLICT (name) DO NOTHING;
