
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
package_root = os.path.dirname(current_dir)
parent_of_package = os.path.dirname(package_root)
sys.path.append(parent_of_package)

try:
    from sherlock_project.sites import SitesInformation
    
    data_path = os.path.join(current_dir, "resources", "data.json")
    sites = SitesInformation(data_path)
    
    for key in sites.sites:
        val = sites.sites[key]
        print(f"Key: {key}")
        print(f"Type: {type(val)}")
        print(f"Dir: {dir(val)}")
        
        # Check if it has urlMain attribute
        if hasattr(val, 'url_main'):
            print(f"url_main: {val.url_main}")
        if hasattr(val, 'urlMain'):
            print(f"urlMain: {val.urlMain}")
            
        # Try converting to dict using vars() or __dict__
        try:
            print(f"vars(): {vars(val)}")
        except:
            print("vars() failed")
            
        break

except Exception as e:
    print(f"Error: {e}")
