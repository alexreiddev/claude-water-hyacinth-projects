package com.expensetracker.data.local.entity

// ANDROID-ONLY (uncomment when migrating to Android + Room):
// import androidx.room.ColumnInfo
// import androidx.room.Entity
// import androidx.room.Index
// import androidx.room.PrimaryKey
//
// @Entity(
//     tableName = "merchants",
//     indices = [Index(value = ["normalized_name"], unique = true)],
// )

/**
 * Normalised merchant record, extracted from transaction descriptions by the ingestion module.
 *
 * SQL schema:
 * ```sql
 * CREATE TABLE merchants (
 *     id              INTEGER PRIMARY KEY AUTOINCREMENT,
 *     normalized_name TEXT    NOT NULL UNIQUE,
 *     display_name    TEXT    NOT NULL,
 *     category_hint   TEXT
 * );
 * ```
 *
 * Design notes:
 * - [normalizedName] is lowercase-trimmed; used as a stable lookup key during ingestion.
 * - [categoryHint] stores a [com.expensetracker.domain.model.Category.name] string and is
 *   used by the categorisation engine as a merchant-level default before falling back to rules/ML.
 *   Nullable because not all merchants have a reliable default category.
 */
data class MerchantEntity(
    // ANDROID-ONLY: @PrimaryKey(autoGenerate = true) @ColumnInfo(name = "id")
    val id: Long = 0L,
    // ANDROID-ONLY: @ColumnInfo(name = "normalized_name")
    val normalizedName: String,
    // ANDROID-ONLY: @ColumnInfo(name = "display_name")
    val displayName: String,
    // ANDROID-ONLY: @ColumnInfo(name = "category_hint")
    val categoryHint: String? = null,
)
