import psycopg


DB_URL = "postgresql://postgres:pgadmin@localhost:5432/genai"

conn = psycopg.connect(DB_URL)
conn.autocommit = True

cur = conn.cursor()

# Add chunking strategy
cur.execute("""
ALTER TABLE document_chunks
ADD COLUMN IF NOT EXISTS chunking_strategy TEXT;
""")

# Add document date
cur.execute("""
ALTER TABLE document_chunks
ADD COLUMN IF NOT EXISTS document_date DATE;
""")

# Set page numbers for scanned handbook
cur.execute("""
UPDATE document_chunks
SET page = 1
WHERE source = 'clinic_patient_handbook_scanned.pdf'
AND section IN (
    '1. Appointment Cancellation',
    '2. Missed Appointments'
);
""")

cur.execute("""
UPDATE document_chunks
SET page = 2
WHERE source = 'clinic_patient_handbook_scanned.pdf'
AND section IN (
    '3. Rescheduling',
    '4. Privacy'
);
""")

# Set strategy for the currently loaded chunks
cur.execute("""
UPDATE document_chunks
SET chunking_strategy = 'structure-aware'
WHERE chunking_strategy IS NULL;
""")

print("Metadata updated successfully.")

cur.close()
conn.close()