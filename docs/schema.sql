CREATE TABLE categories (
	id SERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	description TEXT, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE TABLE users (
	id SERIAL NOT NULL, 
	full_name VARCHAR(150) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	role VARCHAR(30) DEFAULT 'user' NOT NULL, 
	user_type VARCHAR(30) DEFAULT 'student' NOT NULL, 
	group_or_department VARCHAR(100), 
	phone VARCHAR(30), 
	is_blocked BOOLEAN DEFAULT false NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id)
);

CREATE TABLE audit_log (
	id SERIAL NOT NULL, 
	user_id INTEGER, 
	action VARCHAR(100) NOT NULL, 
	entity_type VARCHAR(50) NOT NULL, 
	entity_id INTEGER, 
	details TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE TABLE equipment (
	id SERIAL NOT NULL, 
	category_id INTEGER NOT NULL, 
	name VARCHAR(150) NOT NULL, 
	description TEXT, 
	manufacturer VARCHAR(100), 
	is_active BOOLEAN DEFAULT true NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(category_id) REFERENCES categories (id) ON DELETE RESTRICT
);

CREATE TABLE equipment_photos (
	id SERIAL NOT NULL, 
	equipment_id INTEGER NOT NULL, 
	url VARCHAR(500) NOT NULL, 
	is_main BOOLEAN DEFAULT false NOT NULL, 
	sort_order INTEGER DEFAULT '0' NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(equipment_id) REFERENCES equipment (id) ON DELETE CASCADE
);

CREATE TABLE equipment_units (
	id SERIAL NOT NULL, 
	equipment_id INTEGER NOT NULL, 
	inventory_number VARCHAR(50) NOT NULL, 
	condition VARCHAR(30) DEFAULT 'good' NOT NULL, 
	status VARCHAR(30) DEFAULT 'available' NOT NULL, 
	notes TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(equipment_id) REFERENCES equipment (id) ON DELETE CASCADE, 
	UNIQUE (inventory_number)
);

CREATE TABLE rental_terms (
	id SERIAL NOT NULL, 
	equipment_id INTEGER NOT NULL, 
	max_days INTEGER DEFAULT '7' NOT NULL, 
	deposit NUMERIC(10, 2) DEFAULT '0' NOT NULL, 
	fine_per_day NUMERIC(10, 2) DEFAULT '0' NOT NULL, 
	allowed_for VARCHAR(30) DEFAULT 'all' NOT NULL, 
	requirements TEXT, 
	PRIMARY KEY (id), 
	UNIQUE (equipment_id), 
	FOREIGN KEY(equipment_id) REFERENCES equipment (id) ON DELETE CASCADE
);

CREATE TABLE waitlist_entries (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	equipment_id INTEGER NOT NULL, 
	desired_start DATE NOT NULL, 
	desired_end DATE NOT NULL, 
	status VARCHAR(30) DEFAULT 'waiting' NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	notified_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(equipment_id) REFERENCES equipment (id) ON DELETE CASCADE
);

CREATE TABLE bookings (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	equipment_id INTEGER NOT NULL, 
	unit_id INTEGER, 
	start_date DATE NOT NULL, 
	end_date DATE NOT NULL, 
	status VARCHAR(30) DEFAULT 'pending' NOT NULL, 
	user_comment TEXT, 
	admin_comment TEXT, 
	decided_by INTEGER, 
	decided_at TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_bookings_dates CHECK (end_date >= start_date), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT, 
	FOREIGN KEY(equipment_id) REFERENCES equipment (id) ON DELETE RESTRICT, 
	FOREIGN KEY(unit_id) REFERENCES equipment_units (id) ON DELETE SET NULL, 
	FOREIGN KEY(decided_by) REFERENCES users (id) ON DELETE SET NULL
);

CREATE TABLE booking_status_history (
	id SERIAL NOT NULL, 
	booking_id INTEGER NOT NULL, 
	old_status VARCHAR(30), 
	new_status VARCHAR(30) NOT NULL, 
	changed_by INTEGER, 
	comment TEXT, 
	changed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(booking_id) REFERENCES bookings (id) ON DELETE CASCADE, 
	FOREIGN KEY(changed_by) REFERENCES users (id) ON DELETE SET NULL
);

CREATE TABLE fines (
	id SERIAL NOT NULL, 
	booking_id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	fine_type VARCHAR(30) NOT NULL, 
	amount NUMERIC(10, 2) NOT NULL, 
	days_overdue INTEGER, 
	status VARCHAR(30) DEFAULT 'unpaid' NOT NULL, 
	description TEXT, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	paid_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	FOREIGN KEY(booking_id) REFERENCES bookings (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT
);

CREATE TABLE handovers (
	id SERIAL NOT NULL, 
	booking_id INTEGER NOT NULL, 
	unit_id INTEGER NOT NULL, 
	issued_by INTEGER NOT NULL, 
	issued_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	condition_on_issue VARCHAR(30) NOT NULL, 
	notes TEXT, 
	PRIMARY KEY (id), 
	UNIQUE (booking_id), 
	FOREIGN KEY(booking_id) REFERENCES bookings (id) ON DELETE CASCADE, 
	FOREIGN KEY(unit_id) REFERENCES equipment_units (id) ON DELETE RESTRICT, 
	FOREIGN KEY(issued_by) REFERENCES users (id) ON DELETE RESTRICT
);

CREATE TABLE notifications (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	booking_id INTEGER, 
	type VARCHAR(30) NOT NULL, 
	title VARCHAR(150) NOT NULL, 
	message TEXT NOT NULL, 
	is_read BOOLEAN DEFAULT false NOT NULL, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(booking_id) REFERENCES bookings (id) ON DELETE SET NULL
);

CREATE TABLE returns (
	id SERIAL NOT NULL, 
	booking_id INTEGER NOT NULL, 
	accepted_by INTEGER NOT NULL, 
	returned_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
	condition_on_return VARCHAR(30) NOT NULL, 
	has_damage BOOLEAN DEFAULT false NOT NULL, 
	damage_description TEXT, 
	notes TEXT, 
	PRIMARY KEY (id), 
	UNIQUE (booking_id), 
	FOREIGN KEY(booking_id) REFERENCES bookings (id) ON DELETE CASCADE, 
	FOREIGN KEY(accepted_by) REFERENCES users (id) ON DELETE RESTRICT
);
