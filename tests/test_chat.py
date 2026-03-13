from src.dashboard.chat import extract_sql, validate_sql


def test_extract_sql_from_code_block():
    text = "Aqui va el query:\n```sql\nSELECT * FROM inventory\n```"
    assert extract_sql(text) == "SELECT * FROM inventory"


def test_extract_sql_from_generic_block():
    text = "Resultado:\n```\nSELECT count(*) FROM orders\n```"
    assert extract_sql(text) == "SELECT count(*) FROM orders"


def test_extract_sql_returns_none_without_block():
    text = "No tengo un query para eso."
    assert extract_sql(text) is None


def test_validate_sql_accepts_select():
    assert validate_sql("SELECT * FROM inventory") is True


def test_validate_sql_rejects_drop():
    assert validate_sql("DROP TABLE inventory") is False


def test_validate_sql_rejects_delete():
    assert validate_sql("DELETE FROM inventory") is False


def test_validate_sql_rejects_update():
    assert validate_sql("UPDATE inventory SET x=1") is False


def test_validate_sql_rejects_insert():
    assert validate_sql("INSERT INTO inventory VALUES (1)") is False


def test_validate_sql_rejects_select_with_drop():
    query = "SELECT * FROM inventory; DROP TABLE inventory"
    assert validate_sql(query) is False


def test_validate_sql_case_insensitive():
    assert validate_sql("select * from inventory") is True
    assert validate_sql("drop table inventory") is False
