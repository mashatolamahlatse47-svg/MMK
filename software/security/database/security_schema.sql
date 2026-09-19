PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS security_sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER,
    name TEXT NOT NULL,
    address TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS security_shifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER NOT NULL,
    supervisor_id INTEGER,
    shift_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (site_id) REFERENCES security_sites(id)
);

CREATE TABLE IF NOT EXISTS security_occurrences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER NOT NULL,
    user_id INTEGER,
    occurrence_date TEXT NOT NULL,
    occurrence_time TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    action_taken TEXT,
    status TEXT NOT NULL DEFAULT 'open',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (site_id) REFERENCES security_sites(id)
);

CREATE TABLE IF NOT EXISTS security_incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    occurrence_id INTEGER NOT NULL,
    severity TEXT NOT NULL,
    description TEXT NOT NULL,
    response TEXT,
    resolution TEXT,
    supervisor_id INTEGER,
    status TEXT NOT NULL DEFAULT 'open',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (occurrence_id) REFERENCES security_occurrences(id)
);

CREATE TABLE IF NOT EXISTS security_handovers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER NOT NULL,
    from_user_id INTEGER,
    to_user_id INTEGER,
    shift_id INTEGER,
    handover_date TEXT NOT NULL,
    notes TEXT,
    outstanding_items TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (site_id) REFERENCES security_sites(id),
    FOREIGN KEY (shift_id) REFERENCES security_shifts(id)
);

CREATE INDEX IF NOT EXISTS idx_occurrences_site
ON security_occurrences(site_id);

CREATE INDEX IF NOT EXISTS idx_occurrences_date
ON security_occurrences(occurrence_date);

CREATE INDEX IF NOT EXISTS idx_incidents_occurrence
ON security_incidents(occurrence_id);

CREATE INDEX IF NOT EXISTS idx_shifts_site
ON security_shifts(site_id);

CREATE INDEX IF NOT EXISTS idx_handovers_site
ON security_handovers(site_id);
