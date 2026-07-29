SELECT
    r.tenant_id,
    t.name as tenant_name,
    p.name as property_name,
    SUM(r.total_amount) as revenue,
    COUNT(*) as bookings
FROM
    reservations r
    JOIN properties p ON r.property_id = p.id
    JOIN tenants t ON t.id = r.tenant_id
GROUP BY
    r.tenant_id,
    r.property_id,
    p.name,
    t.name
ORDER BY r.tenant_id, r.property_id