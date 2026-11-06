# seed_data.py — run once from backend/ folder
from app import create_app, db
from app.models import User, Laboratory, Supplier, Equipment, Component, ItemClass
from datetime import date

app = create_app()

with app.app_context():
    # Safety guard: skip if already seeded
    if User.query.first():
        print('⚠️  Database already has data. Delete data/inventory.db to reset.')
        exit()

    # ---------- Users ----------
    users = [
        User(full_name='Abebe Kebede', email='abebe@lab.edu', role='Admin', phone='+251911000001'),
        User(full_name='Sara Tesfaye', email='sara@lab.edu', role='Storekeeper', phone='+251911000002'),
        User(full_name='Daniel Mekonnen', email='daniel@lab.edu', role='Technician', phone='+251911000003'),
        User(full_name='Hana Girma', email='hana@lab.edu', role='Viewer', phone='+251911000004'),
    ]
    for u in users:
        u.set_password('password123')
    db.session.add_all(users)
    db.session.commit()
    print(f'✅ {len(users)} users')

    # ---------- Suppliers ----------
    suppliers = [
        Supplier(supplier_name='TechSource PLC', contact_person='Mulu Alemu', phone='+251922000001', email='sales@techsource.et', address='Addis Ababa'),
        Supplier(supplier_name='ElectroMart Ltd', contact_person='Yonas Bekele', phone='+251922000002', email='info@electromart.et', address='Addis Ababa'),
        Supplier(supplier_name='Global Instruments', contact_person='Ruth Haile', phone='+251922000003', email='orders@globalinst.com', address='Nairobi KE'),
        Supplier(supplier_name='SciSupply Co.', contact_person='Kebede Desta', phone='+251922000004', email='support@scisupply.et', address='Adama'),
    ]
    db.session.add_all(suppliers)
    db.session.commit()
    print(f'✅ {len(suppliers)} suppliers')

    # ---------- Laboratories ----------
    labs = [
        Laboratory(lab_name='Electronics Laboratory', lab_code='ELE-LAB', location='Block A Room 101', supervisor_id=3, description='Analog and digital electronics'),
        Laboratory(lab_name='Electrical Machines Laboratory', lab_code='EMC-LAB', location='Block B Room 205', supervisor_id=3, description='Motors generators transformers'),
        Laboratory(lab_name='Power Systems Laboratory', lab_code='PSL-LAB', location='Block B Room 210', supervisor_id=3, description='Transmission and distribution'),
        Laboratory(lab_name='Control Systems Laboratory', lab_code='CSL-LAB', location='Block C Room 112', supervisor_id=3, description='PLCs controllers sensors'),
        Laboratory(lab_name='Computer Laboratory', lab_code='CMP-LAB', location='Block A Room 305', supervisor_id=3, description='PCs networking software'),
    ]
    db.session.add_all(labs)
    db.session.commit()
    print(f'✅ {len(labs)} laboratories')

    # ---------- Equipment (20) ----------
    equipment_data = [
        ('EQ-0001','Digital Oscilloscope 100MHz','Test Instrument',1,1,'OSC-2024-001',date(2024,3,15),45000,'available','QR-EQ-0001'),
        ('EQ-0002','Function Generator','Test Instrument',1,1,'FG-2024-012',date(2024,3,15),18000,'borrowed','QR-EQ-0002'),
        ('EQ-0003','Three-Phase Induction Motor','Machine',2,2,'MOT-2023-007',date(2023,11,20),65000,'available','QR-EQ-0003'),
        ('EQ-0004','Transformer Trainer Kit','Trainer',3,2,'TRN-2023-003',date(2023,9,10),120000,'under_maintenance','QR-EQ-0004'),
        ('EQ-0005','PLC Trainer S7-1200','Trainer',4,3,'PLC-2024-021',date(2024,1,8),95000,'available','QR-EQ-0005'),
        ('EQ-0006','Desktop PC Core i7','Computer',5,1,'PC-2024-045',date(2024,2,20),55000,'available','QR-EQ-0006'),
        ('EQ-0007','Multimeter Digital','Test Instrument',1,1,'MM-2024-033',date(2024,4,1),3500,'damaged','QR-EQ-0007'),
        ('EQ-0008','DC Power Supply 30V','Test Instrument',1,1,'PS-2023-018',date(2023,8,12),22000,'available','QR-EQ-0008'),
        ('EQ-0009','Single-Phase Transformer','Machine',2,2,'TRF-2023-011',date(2023,10,5),48000,'borrowed','QR-EQ-0009'),
        ('EQ-0010','Arduino Starter Kit','Microcontroller',4,1,'ARD-2024-055',date(2024,5,10),8500,'available','QR-EQ-0010'),
        ('EQ-0011','Network Switch 24-Port','Networking',5,1,'NS-2024-002',date(2024,1,20),32000,'available','QR-EQ-0011'),
        ('EQ-0012','Signal Analyzer','Spectrum',3,3,'SA-2023-009',date(2023,7,18),150000,'available','QR-EQ-0012'),
        ('EQ-0013','Soldering Station','Hobby Tool',1,4,'SS-2024-017',date(2024,2,28),6500,'available','QR-EQ-0013'),
        ('EQ-0014','Three-Phase Motor Controller','Machine',2,2,'MC-2024-023',date(2024,3,12),78000,'available','QR-EQ-0014'),
        ('EQ-0015','Laptop Dell Latitude','Computer',5,1,'LAP-2024-060',date(2024,4,15),72000,'borrowed','QR-EQ-0015'),
        ('EQ-0016','Logic Analyzer','Test Instrument',1,1,'LA-2023-021',date(2023,11,1),38000,'available','QR-EQ-0016'),
        ('EQ-0017','PLC Trainer S7-300','Trainer',4,3,'PLC-2023-008',date(2023,9,22),110000,'under_maintenance','QR-EQ-0017'),
        ('EQ-0018','Power Analyzer','Test Instrument',3,3,'PA-2024-003',date(2024,6,1),85000,'available','QR-EQ-0018'),
        ('EQ-0019','Router Cisco 2901','Networking',5,1,'RT-2024-005',date(2024,2,10),42000,'available','QR-EQ-0019'),
        ('EQ-0020','DC Motor 12V','Machine',2,2,'DM-2024-004',date(2024,1,30),9500,'available','QR-EQ-0020'),
    ]
    for row in equipment_data:
        db.session.add(Equipment(
            asset_tag=row[0], equip_name=row[1], category=row[2], lab_id=row[3],
            supplier_id=row[4], serial_no=row[5], purchase_date=row[6],
            unit_price=row[7], status=row[8], qr_code=row[9]
        ))
    db.session.commit()
    print(f'✅ {len(equipment_data)} equipment')

    # ---------- Components (25) ----------
    components_data = [
        ('Resistor 10kohm','Passive','pcs',500,100,2.50,4,1,'QR-CP-0001'),
        ('Capacitor 100uF','Passive','pcs',80,100,5.00,4,1,'QR-CP-0002'),
        ('LED Red 5mm','Opto','pcs',300,50,1.50,4,1,'QR-CP-0003'),
        ('Arduino Uno R3','Microcontroller','pcs',25,10,1200.00,1,4,'QR-CP-0004'),
        ('Jumper Wires M-M','Connector','pack',40,15,80.00,1,1,'QR-CP-0005'),
        ('Contactor 3-Pole 25A','Electrical','pcs',12,5,950.00,2,2,'QR-CP-0006'),
        ('Breadboard 830pt','Prototyping','pcs',60,20,150.00,1,1,'QR-CP-0007'),
        ('Resistor 1kohm','Passive','pcs',450,100,2.50,4,1,'QR-CP-0008'),
        ('Diode 1N4007','Passive','pcs',600,150,1.20,4,1,'QR-CP-0009'),
        ('Transistor BC547','Active','pcs',350,100,3.00,4,1,'QR-CP-0010'),
        ('IC 555 Timer','Active','pcs',90,30,8.00,3,1,'QR-CP-0011'),
        ('Seven-Segment Display','Opto','pcs',55,20,15.00,1,1,'QR-CP-0012'),
        ('Relay 5V SPDT','Electrical','pcs',120,40,45.00,2,2,'QR-CP-0013'),
        ('Fuse 5A','Protection','pcs',200,50,6.00,2,2,'QR-CP-0014'),
        ('Terminal Block 12-Way','Connector','pcs',35,10,25.00,2,2,'QR-CP-0015'),
        ('Capacitor 10uF','Passive','pcs',220,80,3.50,4,1,'QR-CP-0016'),
        ('Potentiometer 10k','Passive','pcs',75,30,12.00,1,1,'QR-CP-0017'),
        ('Buzzer 5V','Opto','pcs',45,20,18.00,1,1,'QR-CP-0018'),
        ('ESP32 Module','Microcontroller','pcs',15,10,950.00,1,4,'QR-CP-0019'),
        ('Servo Motor SG90','Machine','pcs',30,10,350.00,3,4,'QR-CP-0020'),
        ('Wire 1.5mm Red','Wire','meter',500,200,8.00,2,2,'QR-CP-0021'),
        ('Wire 1.5mm Black','Wire','meter',480,200,8.00,2,2,'QR-CP-0022'),
        ('PCB Copper Board','Prototyping','pcs',40,15,120.00,1,1,'QR-CP-0023'),
        ('USB Cable Type-B','Connector','pcs',28,10,60.00,1,5,'QR-CP-0024'),
        ('Power Cable IEC','Connector','pcs',50,20,75.00,2,5,'QR-CP-0025'),
    ]
    for row in components_data:
        db.session.add(Component(
            comp_name=row[0], category=row[1], unit=row[2], quantity=row[3],
            min_threshold=row[4], unit_price=row[5], supplier_id=row[6],
            lab_id=row[7], qr_code=row[8]
        ))
    db.session.commit()
    print(f'✅ {len(components_data)} components')

    # ---------- Item Classes (image ↔ DB link) ----------
    item_classes = [
        (8,'oscilloscope','equipment',1,0.85,'Digital Oscilloscope 100MHz'),
        (14,'multimeter','equipment',7,0.80,'Multimeter Digital'),
        (4,'arduino_uno','component',4,0.85,'Arduino Uno R3'),
        (7,'breadboard_830','component',7,0.80,'Breadboard 830pt'),
        (3,'led_red_5mm','component',3,0.80,'LED Red 5mm'),
        (1,'resistor_10k','component',1,0.75,'Resistor 10kΩ'),
        (2,'capacitor_100uf','component',2,0.75,'Capacitor 100µF'),
        (9,'function_generator','equipment',2,0.85,'Function Generator'),
        (10,'induction_motor','equipment',3,0.85,'Three-Phase Induction Motor'),
        (12,'plc_trainer','equipment',5,0.85,'PLC Trainer S7-1200'),
        (5,'jumper_wires','component',5,0.70,'Jumper Wires (M-M)'),
        (6,'contactor_3pole','component',6,0.80,'Contactor 3-Pole 25A'),
    ]
    for row in item_classes:
        db.session.add(ItemClass(
            class_id=row[0], class_name=row[1], item_type=row[2],
            item_id=row[3], confidence_threshold=row[4], display_name=row[5]
        ))
    db.session.commit()
    print(f'✅ {len(item_classes)} item classes')

    print('\n🎉 Seeding complete.')
    print(f'   Users: {User.query.count()}')
    print(f'   Suppliers: {Supplier.query.count()}')
    print(f'   Laboratories: {Laboratory.query.count()}')
    print(f'   Equipment: {Equipment.query.count()}')
    print(f'   Components: {Component.query.count()}')
    print(f'   Item Classes: {ItemClass.query.count()}')