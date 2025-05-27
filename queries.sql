-- Source db ddl:

create database eswatini
go;

create table eswatini.dbo.client (
    id bigint identity(1,1) primary key,
    first_name VARCHAR not null,
    last_name VARCHAR not null,
    date_of_birth date not null,
    is_verified bit,
    phone_number varchar not null unique
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
    transaction_type varchar not null,
    transaction_date datetime not null,
    amount money not null,
    loan_id bigint not null,

    foreign key (loan_id) references loan(id) on delete cascade
);

create table eswatini.dbo.charges (
    id bigint identity(1,1) primary key,
    name varchar not null unique,
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

create table eswatini.dbo.dummy (
    id bigint identity(1,1) primary key,
    text varchar not null
)