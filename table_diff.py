from utils import index_list_by_key


def are_tables_equal(expected_table, actual_table, silent=False):
    for dst in expected_table:
        expected_entry = expected_table[dst]
        if dst not in actual_table:
            if not silent: print(f"{dst} not in actual_table")
            return False
        actual_entry = actual_table[dst]
        if "nexthops" in expected_entry and "nexthops" in actual_entry:
            expected_next_hops = index_list_by_key(
                list=expected_entry["nexthops"], key="gateway"
            )
            actual_next_hops = index_list_by_key(
                list=actual_entry["nexthops"], key="gateway"
            )
            for next_hop_gateway in expected_next_hops:
                if next_hop_gateway not in actual_next_hops:
                    if not silent: print(f"{next_hop_gateway} not in actual next hops")
                    return False
        elif "gateway" in expected_entry and "gateway" in actual_entry:
            if expected_entry["gateway"] != actual_entry["gateway"]:
                return False
        elif "prefsrc" in expected_entry and "prefsrc" in actual_entry:
            if expected_entry["prefsrc"] != actual_entry["prefsrc"]:
                if not silent: print("prefsrc")
                return False
        else:
            raise RuntimeError(f"Unexpected entry structure for dst {dst}")
    return True
