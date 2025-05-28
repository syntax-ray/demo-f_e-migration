-- Source db ddl:

create database source_db
go;

create table eswatini.dbo.client (
    id bigint identity(1,1) primary key,
    first_name VARCHAR(50) not null,
    last_name VARCHAR(50) not null,
    date_of_birth date not null,
    is_verified bit,
    phone_number varchar(20) not null unique
);

create table eswatini.dbo.loan (
    id bigint identity(1,1) primary key,
    amount money not null,
    effective_date datetime not null,
    status int not null,
    client_id bigint not null,

    foreign key (client_id) references client(id) on delete cascade
);

create table eswatini.dbo.transactions (
    id bigint identity(1,1) primary key,
    transaction_type varchar(20) not null,
    transaction_date datetime not null,
    amount money not null,
    loan_id bigint not null,

    foreign key (loan_id) references loan(id) on delete cascade
);

create table eswatini.dbo.charges (
    id bigint identity(1,1) primary key,
    name varchar(20) not null unique,
    amount money
);

create table eswatini.dbo.loan_charges (
    id bigint identity(1,1) primary key,
    amount money not null,
    charge_id bigint not null,
    loan_id bigint not null,

    foreign key (loan_id) references loan(id) on delete cascade,
    foreign key (charge_id) references charges(id) on delete cascade
);

-- dummy table for testing purposes ie: can this table be ommitted from the migration?
create table eswatini.dbo.dummy (
    id bigint identity(1,1) primary key,
    text varchar(20) not null
);


-- source data dml

-- insert 1000 clients.
DECLARE @i INT = 1;
WHILE @i <= 1000
    BEGIN
        INSERT INTO eswatini.dbo.client (first_name, last_name, date_of_birth, is_verified, phone_number)
        VALUES (
                   'First' + CAST(@i AS VARCHAR),
                   'Last' + CAST(@i AS VARCHAR),
                   DATEADD(DAY, -1 * (365 * (20 + ABS(CHECKSUM(NEWID())) % 30)), GETDATE()),
                   CASE WHEN @i % 2 = 0 THEN 1 ELSE 0 END,
                   '07' + RIGHT('0000000' + CAST(@i AS VARCHAR), 7)
               );
        SET @i += 1;
    END

-- insert client loans.
DECLARE @client_id BIGINT;
DECLARE loan_cursor CURSOR FOR SELECT id FROM eswatini.dbo.client;

OPEN loan_cursor;
FETCH NEXT FROM loan_cursor INTO @client_id;

WHILE @@FETCH_STATUS = 0
    BEGIN
        DECLARE @j INT = 1;
        WHILE @j <= (1 + ABS(CHECKSUM(NEWID())) % 3)
            BEGIN
                INSERT INTO eswatini.dbo.loan (amount, effective_date, status, client_id)
                VALUES (
                           (1000 + ABS(CHECKSUM(NEWID())) % 10000),
                           DATEADD(DAY, -1 * (ABS(CHECKSUM(NEWID())) % 365), GETDATE()),
                           ABS(CHECKSUM(NEWID())) % 4,
                           @client_id
                       );
                SET @j += 1;
            END
        FETCH NEXT FROM loan_cursor INTO @client_id;
    END

CLOSE loan_cursor;
DEALLOCATE loan_cursor;

-- insert charges
DECLARE @k INT = 1;
WHILE @k <= 20
BEGIN
    INSERT INTO eswatini.dbo.charges (name, amount)
    VALUES (
        'Charge ' + CAST(@k AS VARCHAR),
        (10 + ABS(CHECKSUM(NEWID())) % 100)
    );
    SET @k += 1;
END;

-- insert loan charges and loan transactions.
DECLARE @loan_id BIGINT;
DECLARE trans_cursor CURSOR FOR SELECT id FROM eswatini.dbo.loan;

OPEN trans_cursor;
FETCH NEXT FROM trans_cursor INTO @loan_id;

WHILE @@FETCH_STATUS = 0
BEGIN
    -- Insert Transactions
    DECLARE @t INT = 1;
    WHILE @t <= (1 + ABS(CHECKSUM(NEWID())) % 5)
    BEGIN
        INSERT INTO eswatini.dbo.transactions (transaction_type, transaction_date, amount, loan_id)
        VALUES (
            CASE WHEN @t % 2 = 0 THEN 'CREDIT' ELSE 'DEBIT' END,
            DATEADD(DAY, -1 * (ABS(CHECKSUM(NEWID())) % 365), GETDATE()),
            (100 + ABS(CHECKSUM(NEWID())) % 1000),
            @loan_id
        );
        SET @t += 1;
    END

    -- Insert Loan Charges (1–2 charges per loan)
    DECLARE @c INT = 1;
    WHILE @c <= (1 + ABS(CHECKSUM(NEWID())) % 2)
    BEGIN
        INSERT INTO eswatini.dbo.loan_charges (amount, charge_id, loan_id)
        VALUES (
            (10 + ABS(CHECKSUM(NEWID())) % 50),
            1 + ABS(CHECKSUM(NEWID())) % 20,
            @loan_id
        );
        SET @c += 1;
    END

    FETCH NEXT FROM trans_cursor INTO @loan_id;
END

CLOSE trans_cursor;
DEALLOCATE trans_cursor;


-- insert dummy table data.
DECLARE @d INT = 1;
WHILE @d <= 1000
BEGIN
    INSERT INTO eswatini.dbo.dummy (text)
    VALUES ('Dummy Text ' + CAST(@d AS VARCHAR));
    SET @d += 1;
END;
