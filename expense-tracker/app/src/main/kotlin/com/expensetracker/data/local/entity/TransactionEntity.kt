package com.expensetracker.data.local.entity

// ANDROID-ONLY (uncomment when migrating to Android + Room):
// import androidx.room.ColumnInfo
// import androidx.room.Entity
// import androidx.room.ForeignKey
// import androidx.room.Index
// import androidx.room.PrimaryKey
//
// @Entity(
//     tableName = "transactions",
//     foreignKeys = [
//         ForeignKey(
//             entity = MerchantEntity::class,
//             parentColumns = ["id"],
//             childColumns = ["merchant_id"],
//             onDelete = ForeignKey.SET_NULL,
//         ),
//     ],
//     indices = [
//         Index("category"),
//         Index("timestamp_millis"),
//         Index("merchant_id"),
//     ],
// )

/**
 * Persisted form of [com.expensetracker.domain.model.Expense].
 *
 * SQL schema:
 * ```sql
 * CREATE TABLE transactions (
 *     id               INTEGER PRIMARY KEY AUTOINCREMENT,
 *     amount_text      TEXT    NOT NULL,
 *     description      TEXT    NOT NULL,
 *     category         TEXT    NOT NULL,
 *     tags_json        TEXT    NOT NULL DEFAULT '[]',
 *     merchant_id      INTEGER REFERENCES merchants(id) ON DELETE SET NULL,
 *     source           TEXT    NOT NULL,
 *     timestamp_millis INTEGER NOT NULL
 * );
 * CREATE INDEX idx_tx_category  ON transactions(category);
 * CREATE INDEX idx_tx_timestamp ON transactions(timestamp_millis DESC);
 * ```
 *
 * Design notes:
 * - [amountText] stores [java.math.BigDecimal.toPlainString] — never REAL/FLOAT for money.
 * - [category] stores [com.expensetracker.domain.model.Category.name] (text, not ordinal)
 *   so schema survives enum reordering.
 * - [tagsJson] stores a JSON array produced by kotlinx-serialization, e.g. `["work","lunch"]`.
 * - [timestampMillis] is [java.time.Instant.toEpochMilli] — timezone-independent and sortable.
 */
data class TransactionEntity(
    // ANDROID-ONLY: @PrimaryKey(autoGenerate = true) @ColumnInfo(name = "id")
    val id: Long = 0L,
    // ANDROID-ONLY: @ColumnInfo(name = "amount_text")
    val amountText: String,
    // ANDROID-ONLY: @ColumnInfo(name = "description")
    val description: String,
    // ANDROID-ONLY: @ColumnInfo(name = "category")
    val category: String,
    // ANDROID-ONLY: @ColumnInfo(name = "tags_json")
    val tagsJson: String = "[]",
    // ANDROID-ONLY: @ColumnInfo(name = "merchant_id")
    val merchantId: Long? = null,
    // ANDROID-ONLY: @ColumnInfo(name = "source")
    val source: String,
    // ANDROID-ONLY: @ColumnInfo(name = "timestamp_millis")
    val timestampMillis: Long,
)
