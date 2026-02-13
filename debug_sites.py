
import sys
import os
# Add the directory containing 'sherlock_project' to sys.path just in case, though it seems installed in site-packages
current_dir = os.path.dirname(os.path.abspath(__file__))
package_root = os.path.dirname(current_dir)
parent_of_package = os.path.dirname(package_root)
sys.path.append(parent_of_package)

try:
    from sherlock_project.sites import SitesInformation
    print("SitesInformation imported successfully.")
    
    data_path = os.path.join(current_dir, "resources", "data.json")
    print(f"Loading data from: {data_path}")
    
    sites = SitesInformation(data_path)
    print(f"Type of sites object: {type(sites)}")
    
    if hasattr(sites, 'sites'):
        print(f"Type of sites.sites: {type(sites.sites)}")
        # Print first key or type of content
        try:
            for key in sites.sites:
                val = sites.sites[key]
                print(f"Key: {key}, Value Type: {type(val)}")
                break
        except Exception as e:
            print(f"Error iterating sites.sites: {e}")
            
    else:
        print("sites object does not have 'sites' attribute.")
        print(f"Dir(sites): {dir(sites)}")

except Exception as e:
    print(f"Error: {e}")
