package com.expensetracker.data.local.entity

import com.expensetracker.domain.model.Category

// ANDROID-ONLY (uncomment when migrating to Android + Room):
// import androidx.room.ColumnInfo
// import androidx.room.Entity
// import androidx.room.PrimaryKey
//
// @Entity(tableName = "categories")

/**
 * Display metadata for each [Category] enum value.
 *
 * The primary key [id] is the [Category.name] string (e.g. `"FOOD"`), not an auto-increment
 * integer. This makes the implicit FK from [TransactionEntity.category] trivially resolvable
 * without a JOIN and survives database recreation as long as enum names are stable.
 *
 * SQL schema:
 * ```sql
 * CREATE TABLE categories (
 *     id           TEXT PRIMARY KEY,
 *     display_name TEXT NOT NULL,
 *     icon_key     TEXT NOT NULL,
 *     color_hex    TEXT NOT NULL
 * );
 * ```
 */
data class CategoryEntity(
    // ANDROID-ONLY: @PrimaryKey @ColumnInfo(name = "id")
    val id: String,
    // ANDROID-ONLY: @ColumnInfo(name = "display_name")
    val displayName: String,
    // ANDROID-ONLY: @ColumnInfo(name = "icon_key")
    val iconKey: String,
    // ANDROID-ONLY: @ColumnInfo(name = "color_hex")
    val colorHex: String,
) {
    companion object {
        /** One pre-seeded row per [Category] enum constant. Insert at DB creation time. */
        fun seedData(): List<CategoryEntity> =
            listOf(
                CategoryEntity(Category.FOOD.name, "Food & Dining", "ic_food", "#FF5733"),
                CategoryEntity(Category.TRANSPORT.name, "Transport", "ic_transport", "#3498DB"),
                CategoryEntity(Category.UTILITIES.name, "Utilities", "ic_utilities", "#2ECC71"),
                CategoryEntity(Category.ENTERTAINMENT.name, "Entertainment", "ic_entertainment", "#9B59B6"),
                CategoryEntity(Category.HEALTH.name, "Health", "ic_health", "#E74C3C"),
                CategoryEntity(Category.SHOPPING.name, "Shopping", "ic_shopping", "#F39C12"),
                CategoryEntity(Category.OTHER.name, "Other", "ic_other", "#95A5A6"),
            )
    }
}
