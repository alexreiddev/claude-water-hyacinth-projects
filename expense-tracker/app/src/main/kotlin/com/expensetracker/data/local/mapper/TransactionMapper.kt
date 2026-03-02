package com.expensetracker.data.local.mapper

import com.expensetracker.data.local.entity.TransactionEntity
import com.expensetracker.domain.model.Category
import com.expensetracker.domain.model.Expense
import com.expensetracker.domain.model.IngestionSource
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.math.BigDecimal
import java.time.Instant

private val json = Json { ignoreUnknownKeys = true }

/**
 * Maps a [TransactionEntity] (data layer) to an [Expense] (domain layer).
 *
 * Conversions:
 * - [TransactionEntity.amountText] → [Expense.amount]: parsed as [BigDecimal] (exact decimal).
 * - [TransactionEntity.tagsJson] → [Expense.tags]: deserialized from a JSON string array.
 * - [TransactionEntity.timestampMillis] → [Expense.timestamp]: [Instant.ofEpochMilli].
 * - [TransactionEntity.category] → [Expense.category]: [Category.valueOf].
 * - [TransactionEntity.source] → [Expense.source]: [IngestionSource.valueOf].
 */
fun TransactionEntity.toDomain(): Expense =
    Expense(
        id = id,
        amount = BigDecimal(amountText),
        description = description,
        category = Category.valueOf(category),
        tags = json.decodeFromString<List<String>>(tagsJson),
        source = IngestionSource.valueOf(source),
        timestamp = Instant.ofEpochMilli(timestampMillis),
    )

/**
 * Maps an [Expense] (domain layer) to a [TransactionEntity] (data layer).
 *
 * @param merchantId optional resolved merchant id; null if not yet linked (default for Module 1).
 *
 * Conversions:
 * - [Expense.amount] → [TransactionEntity.amountText]: [BigDecimal.toPlainString] (no scientific notation).
 * - [Expense.tags] → [TransactionEntity.tagsJson]: serialized as a JSON string array.
 * - [Expense.timestamp] → [TransactionEntity.timestampMillis]: [Instant.toEpochMilli].
 * - [Expense.category] → [TransactionEntity.category]: [Category.name].
 * - [Expense.source] → [TransactionEntity.source]: [IngestionSource.name].
 */
fun Expense.toEntity(merchantId: Long? = null): TransactionEntity =
    TransactionEntity(
        id = id,
        amountText = amount.toPlainString(),
        description = description,
        category = category.name,
        tagsJson = json.encodeToString(tags),
        merchantId = merchantId,
        source = source.name,
        timestampMillis = timestamp.toEpochMilli(),
    )
