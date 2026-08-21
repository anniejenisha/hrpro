import frappe

@frappe.whitelist()
def get_workspace_sidebar(workspace_sidebar_name):
    """Fetch structured sidebar items safely using .get() to prevent AttributeErrors."""
    if not frappe.db.exists("Workspace Sidebar", workspace_sidebar_name):
        return []

    doc = frappe.get_doc("Workspace Sidebar", workspace_sidebar_name)
    items = []

    for item in doc.items:
        # Safely extract values regardless of schema naming variants
        child_flag = (
            item.get("child_items") or 
            item.get("child_item") or 
            item.get("is_child") or 
            0
        )
        
        items.append({
            "label": item.get("label") or item.get("link_to"),
            "link_type": item.get("link_type"),
            "type": item.get("type") or "Link",
            "link_to": item.get("link_to"),
            "icon": item.get("icon"),
            "child_item": bool(child_flag)
        })

    return items