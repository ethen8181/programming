insert into jpa_user (id, birth_date, name) values (10001, sysdate(), 'name1');
insert into jpa_user (id, birth_date, name) values (10002, sysdate(), 'name2');
insert into jpa_user (id, birth_date, name) values (10003, sysdate(), 'name3');
insert into jpa_post (id, description, jpa_user_id) values (20001, 'My First Post', 10001);
insert into jpa_post (id, description, jpa_user_id) values (20002, 'My Second Post', 10001);