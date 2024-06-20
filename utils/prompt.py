i2b2_2006_prompt="""
    Please extract the following things into a structured data from the given sentence if present:
    
    Patients: includes the first and last names of patients, their health proxies, and family members. It excludes titles, such as Mrs., e.g., Mrs. [Mary Joe] was admitted, Mrs. [Petter Deo] has blurred vision...

    Doctors: refers to medical doctors and other practitioners mentioned in the records. For transcribed records, it includes the transcribers' names and initials. It excludes titles, such as Dr. and M.D., e.g., He met with Dr. [John Bland] , M.D.

    Hospitals: marks the names of medical organizations and of nursing homes where patients are treated and may also reside. It includes room numbers of patients, and buildings and floors related to doctors' affiliations, e.g., The patient was transferred to [Gates 4].

    IDs: refers to any combination of numbers, letters, and special characters identifying medical records, patients, doctors, or hospitals, e.g., Provider Number : [12344].

    Dates: includes all elements of a date except for the year. HIPAA specifies that years are not considered PHI. Therefore, we exclude them from this category. Extract only and only dates and months, do not extract year, day, any time, or othr entities related to Dates.

    Locations: includes geographic locations such as cities, states, countries, street names, zip codes, building names, and numbers, e.g., He lives in [Newton].

    Phone numbers: includes telephone, pager, and fax numbers.

    Ages: includes ages above 90. HIPAA dictates that ages above 90 should be collected under one category, and should be marked as PHI. Ages below 90 can be left as is.
    
    Take a time and Keep in mind the following rules for extraction of entities for each feilds: 
        - If any of the above infomation is not present then simply just return empty list for those feilds. 
        - Make sure to extract all the information regarding all the above feilds should be in as it is form as present in the sentence, e.g; entity "X , Y" should be extracted as it is, not as  "X, Y", "X ,Y", "X", "Y" or any other forms. Here there might be different punctuation present insted of  ","  but the rule is same for each punctuation ,arks.
    sentence : "{sentence}"
"""

i2b2_2014_prompt="""
    Please extract the following things into a structured data from the given clinical note if present:
        1. names: extract the following type of names. Ignore initials like Mr., Mrs., M.D., etc.
            types of names should be: PATIENT NAME, DOCTOR NAME, USERNAME.
        2. professions
        3. locations:
            types of locations should be: ROOM NUMBER, DEPARTMENT NAME, HOSPITAL NAME, ORGANIZATION NAME, STREET NAME, CITY NAME, STATE NAME, COUNTRY NAME, ZIPCODE.
        4. ages
        5. dates
        6. contacts
            types of contacts should be: PHONE NUMBER, FAX NUMBER, EMAIL ADDRESS, URL, IPADDRESS, PAGER NUMBER.
        7. ids:
            types of ids should be: SOCIAL SECURITY NUMBER, MEDICAL RECORD NUMBER, HEALTH PLAN NUMBER, ACCOUNT NUMBER, LICENSE NUMBER, VEHICLE ID, DEVICE ID, BIOMETRIC ID, ID NUMBER
        ---
        clinical note : "{sentence}"
"""