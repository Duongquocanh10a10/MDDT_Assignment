import pcbnew
import sys
import os

pcb_path = r"A:\DEVICE\KiCad_Project\WaterSensor.kicad_pcb"
if not os.path.exists(pcb_path):
    print(f"Error: File not found: {pcb_path}")
    sys.exit(1)

print(f"=== REFILLING ALL COPPER ZONES ===")
print(f"Loading board: {pcb_path}")
board = pcbnew.LoadBoard(pcb_path)

zones = board.Zones()
print(f"Total zones found: {len(zones)}")
for i, zone in enumerate(zones):
    layer_name = board.GetLayerName(zone.GetLayer())
    net_name = zone.GetNetname()
    is_keepout = zone.GetIsRuleArea() if hasattr(zone, 'GetIsRuleArea') else False
    if is_keepout:
        print(f"  [{i}] KEEPOUT zone on {layer_name}")
    else:
        print(f"  [{i}] COPPER zone: Net '{net_name}' on Layer '{layer_name}'")

print("\nExecuting pcbnew.ZONE_FILLER...")
filler = pcbnew.ZONE_FILLER(board)
success = filler.Fill(zones)
print(f"ZONE_FILLER completed: success={success}")

print(f"Saving refilled board back to {pcb_path}...")
board.Save(pcb_path)
print("=== SUCCESS: ALL ZONES REFILLED AND SAVED ===")
