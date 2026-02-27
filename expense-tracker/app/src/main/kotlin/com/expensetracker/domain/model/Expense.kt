package com.expensetracker.domain.model

import java.math.BigDecimal
import java.time.Instant

data class Expense(
    val id: Long = 0,
    val amount: BigDecimal,
    val description: String,
    val category: Category,
    val tags: List<String> = emptyList(),
    val source: IngestionSource,
    val timestamp: Instant,
)

enum class Category {
    FOOD,
    TRANSPORT,
    UTILITIES,
    ENTERTAINMENT,
    HEALTH,
    SHOPPING,
    OTHER,
}

enum class IngestionSource {
    SMS,
    NOTIFICATION,
    PDF,
    MANUAL,
}
