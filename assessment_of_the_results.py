import pandas as pd

df = pd.read_excel('./ISOC_result/Living_room_11/Living_room_11_result.xlsx', header=1)

df["Coverage Ratio"] = df["Coverage (%)"] / 100
df["Coverage Efficiency"] = df["Covered_area (cells)"] / df["Route distance"]
df["Performance Index"] = df["Coverage Ratio"] * df["Coverage Efficiency"]

# Csak a kívánt oszlopokat kiválasztjuk
eredmeny_df = df[["Angle degree", "Robot_size", "Coverage Ratio", "Coverage Efficiency", "Performance Index"]]

# Kerekítés két tizedesre
eredmeny_df[["Coverage Ratio", "Coverage Efficiency", "Performance Index"]] = eredmeny_df[["Coverage Ratio", "Coverage Efficiency", "Performance Index"]].round(4)

# CSV fájlba mentés
eredmeny_df.to_csv("./ISOC_result/Living_room_11/Living_room_result_of_performance_index.csv", index=False)


# Legjobb eredmény kiválasztása
best_row = df.loc[df["Performance Index"].idxmax()]

# Csak az érdekes oszlopok
output_df = df[["Angle degree", "Performance Index"]].sort_values(by="Performance Index", ascending=False)

# Kiíratás
print(output_df)
print("\nBest configuration:\n", best_row)
print(eredmeny_df)