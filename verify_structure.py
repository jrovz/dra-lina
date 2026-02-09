from app import create_app
import os
import sys

def test_app_structure():
    print("Initializing app...", flush=True)
    try:
        app = create_app('testing')
    except Exception as e:
        print(f"FAILED: Could not create app. Error: {e}", flush=True)
        return

    print("App created successfully.", flush=True)
    
    print(f"App root path: {app.root_path}", flush=True)
    
    expected_template_folder = os.path.join(app.root_path, 'templates')
    if os.path.exists(expected_template_folder):
        print(f"SUCCESS: Template folder found at {expected_template_folder}", flush=True)
    else:
        print(f"FAILED: Template folder NOT found at {expected_template_folder}", flush=True)

    client = app.test_client()
    try:
        # Use a route that doesn't query DB immediately on GET
        target_route = '/admin/login' 
        print(f"Attempting to fetch '{target_route}'...", flush=True)
        response = client.get(target_route)
        print(f"Response status: {response.status_code}", flush=True)
        
        if response.status_code == 200:
             print(f"SUCCESS: Route '{target_route}' returned 200 OK.", flush=True)
        elif response.status_code == 500:
             print(f"WARNING: Route '{target_route}' returned 500.", flush=True)
        else:
             print(f"WARNING: Unexpected status {response.status_code}", flush=True)

    except Exception as e:
        print(f"ERROR: Exception during request: {e}", flush=True)

if __name__ == "__main__":
    test_app_structure()
