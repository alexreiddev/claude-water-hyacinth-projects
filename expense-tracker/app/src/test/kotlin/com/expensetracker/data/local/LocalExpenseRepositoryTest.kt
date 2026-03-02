package com.expensetracker.data.local

import com.expensetracker.data.local.dao.FakeTransactionDao
import com.expensetracker.domain.model.Category
import com.expensetracker.domain.model.Expense
import com.expensetracker.domain.model.IngestionSource
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.runTest
import java.math.BigDecimal
import java.time.Instant
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import kotlin.test.assertTrue

class LocalExpenseRepositoryTest {
    private val dao = FakeTransactionDao()
    private val repository = LocalExpenseRepository(dao)

    // ── helpers ──────────────────────────────────────────────────────────────

    private fun expense(
        id: Long = 0L,
        amount: String = "10.00",
        description: String = "Coffee",
        category: Category = Category.FOOD,
        tags: List<String> = emptyList(),
        source: IngestionSource = IngestionSource.MANUAL,
        timestamp: Instant = Instant.ofEpochMilli(1_700_000_000_000L),
    ) = Expense(
        id = id,
        amount = BigDecimal(amount),
        description = description,
        category = category,
        tags = tags,
        source = source,
        timestamp = timestamp,
    )

    // ── tests ─────────────────────────────────────────────────────────────────

    @Test
    fun `save returns a positive generated id`() =
        runTest {
            val id = repository.save(expense())
            assertTrue(id > 0, "Expected a positive id, got $id")
        }

    @Test
    fun `getById returns saved expense`() =
        runTest {
            val id = repository.save(expense(description = "Lunch"))
            val result = repository.getById(id)
            assertNotNull(result)
            assertEquals("Lunch", result.description)
        }

    @Test
    fun `getById returns null for unknown id`() =
        runTest {
            assertNull(repository.getById(9999L))
        }

    @Test
    fun `getAll emits saved expenses`() =
        runTest {
            repository.save(expense(description = "A"))
            repository.save(expense(description = "B"))
            val all = repository.getAll().first()
            assertEquals(2, all.size)
        }

    @Test
    fun `getAll emits updated list after delete`() =
        runTest {
            val id = repository.save(expense(description = "To delete"))
            repository.save(expense(description = "To keep"))
            repository.delete(id)
            val all = repository.getAll().first()
            assertEquals(1, all.size)
            assertEquals("To keep", all.first().description)
        }

    @Test
    fun `getByCategory filters correctly`() =
        runTest {
            repository.save(expense(description = "Bus", category = Category.TRANSPORT))
            repository.save(expense(description = "Pizza", category = Category.FOOD))
            repository.save(expense(description = "Train", category = Category.TRANSPORT))

            val transport = repository.getByCategory(Category.TRANSPORT).first()
            assertEquals(2, transport.size)
            assertTrue(transport.all { it.category == Category.TRANSPORT })
        }

    @Test
    fun `searchByDescription returns case-insensitive matches`() =
        runTest {
            repository.save(expense(description = "Starbucks Coffee"))
            repository.save(expense(description = "Amazon Prime"))
            repository.save(expense(description = "COFFEE BEAN"))

            val results = repository.searchByDescription("coffee")
            assertEquals(2, results.size)
            assertTrue(results.all { it.description.contains("coffee", ignoreCase = true) })
        }

    @Test
    fun `save round-trips BigDecimal amount with full precision`() =
        runTest {
            val precise = BigDecimal("123456789.99")
            val id = repository.save(expense(amount = precise.toPlainString()))
            val result = repository.getById(id)
            assertNotNull(result)
            assertEquals(0, precise.compareTo(result.amount), "Amount precision lost on round-trip")
        }

    @Test
    fun `save round-trips tags list`() =
        runTest {
            val tags = listOf("work", "reimbursable", "london")
            val id = repository.save(expense(tags = tags))
            val result = repository.getById(id)
            assertNotNull(result)
            assertEquals(tags, result.tags)
        }

    @Test
    fun `save round-trips Instant timestamp at millisecond precision`() =
        runTest {
            val ts = Instant.ofEpochMilli(1_700_123_456_789L)
            val id = repository.save(expense(timestamp = ts))
            val result = repository.getById(id)
            assertNotNull(result)
            assertEquals(ts, result.timestamp)
        }

    @Test
    fun `save with existing id updates the record`() =
        runTest {
            val id = repository.save(expense(description = "Original"))
            repository.save(expense(id = id, description = "Updated"))
            val all = repository.getAll().first()
            assertEquals(1, all.size)
            assertEquals("Updated", all.first().description)
        }

    @Test
    fun `getAll flow emits on save without explicit collect restart`() =
        runTest {
            val flow = repository.getAll()
            assertEquals(0, flow.first().size)
            repository.save(expense(description = "New"))
            assertEquals(1, flow.first().size)
        }
}
