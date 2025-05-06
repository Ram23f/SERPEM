from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE usuarios_empresa ADD COLUMN usuario_id INTEGER;",
            reverse_sql="ALTER TABLE usuarios_empresa DROP COLUMN usuario_id;"
        ),
    ]