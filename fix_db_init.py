"""Fix the database initialization code in main.py"""
import re

filepath = "ai-service/main.py"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old = '''            # Step 4: Initialize database + run migrations
            print("\\n🗄️  Step 4: Initializing database...")
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(database.initialize())
                if database.is_ready:
                    print(f"   ✅ Database ready (PostgreSQL: {database.is_postgres})")
                    # Run migrations automatically
                    print("   🔄 Running schema migrations...")
                    try:
                        from database.run_migrations import run_migrations
                        loop.run_until_complete(run_migrations())
                    except Exception as mig_err:
                        print(f"   ⚠️  Migration warning: {mig_err}")
                else:
                    print("   ⚠️  Database not ready")
            except Exception as db_err:
                print(f"   ⚠️  Database init: {db_err}")'''

new = '''            # Step 4: Initialize database + run migrations
            print("\\n🗄️  Step 4: Initializing database...")
            try:
                await database.initialize()
                if database.is_ready:
                    print(f"   ✅ Database ready (PostgreSQL: {database.is_postgres})")
                    # Run migrations automatically
                    print("   🔄 Running schema migrations...")
                    try:
                        from database.run_migrations import run_migrations
                        await run_migrations()
                    except Exception as mig_err:
                        print(f"   ⚠️  Migration warning: {mig_err}")
                else:
                    print("   ⚠️  Database not ready")
            except Exception as db_err:
                print(f"   ⚠️  Database init: {db_err}")'''

if old in content:
    content = content.replace(old, new)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Fixed database init code - replaced loop.run_until_complete with await")
else:
    print("❌ Old text not found. Searching for context...")
    # Find the Step 4 section
    match = re.search(r'# Step 4: Initialize database.*?(?=# Step 4b)', content, re.DOTALL)
    if match:
        section = match.group()
        print("Found section:")
        print(section)
    else:
        print("Could not find Step 4 section at all")
