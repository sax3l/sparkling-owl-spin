export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "13.0.4"
  }
  public: {
    Tables: {
      about_me: {
        Row: {
          created_at: string
          full_text: string | null
          id: string
          intro: string | null
          job_title: string | null
          profile_image_url: string | null
          subtitle: string | null
          title: string | null
          updated_at: string
        }
        Insert: {
          created_at?: string
          full_text?: string | null
          id?: string
          intro?: string | null
          job_title?: string | null
          profile_image_url?: string | null
          subtitle?: string | null
          title?: string | null
          updated_at?: string
        }
        Update: {
          created_at?: string
          full_text?: string | null
          id?: string
          intro?: string | null
          job_title?: string | null
          profile_image_url?: string | null
          subtitle?: string | null
          title?: string | null
          updated_at?: string
        }
        Relationships: []
      }
      articles: {
        Row: {
          content: string | null
          created_at: string
          id: string
          published: boolean
          title: string
          updated_at: string
        }
        Insert: {
          content?: string | null
          created_at?: string
          id?: string
          published?: boolean
          title: string
          updated_at?: string
        }
        Update: {
          content?: string | null
          created_at?: string
          id?: string
          published?: boolean
          title?: string
          updated_at?: string
        }
        Relationships: []
      }
      billing_info: {
        Row: {
          billing_address: string | null
          billing_city: string | null
          billing_country: string | null
          billing_postal_code: string | null
          company_name: string | null
          created_at: string
          id: string
          org_number: string | null
          updated_at: string
          user_id: string
          vat_number: string | null
        }
        Insert: {
          billing_address?: string | null
          billing_city?: string | null
          billing_country?: string | null
          billing_postal_code?: string | null
          company_name?: string | null
          created_at?: string
          id?: string
          org_number?: string | null
          updated_at?: string
          user_id: string
          vat_number?: string | null
        }
        Update: {
          billing_address?: string | null
          billing_city?: string | null
          billing_country?: string | null
          billing_postal_code?: string | null
          company_name?: string | null
          created_at?: string
          id?: string
          org_number?: string | null
          updated_at?: string
          user_id?: string
          vat_number?: string | null
        }
        Relationships: []
      }
      companies: {
        Row: {
          company_form: string | null
          company_id: number
          county_seat: string | null
          created_at: string
          email: string | null
          industry: string | null
          municipal_seat: string | null
          name: string | null
          org_number: string | null
          registration_date: string | null
          remark_control: string | null
          sni_code: string | null
          status: string | null
          updated_at: string
          website: string | null
        }
        Insert: {
          company_form?: string | null
          company_id?: number
          county_seat?: string | null
          created_at?: string
          email?: string | null
          industry?: string | null
          municipal_seat?: string | null
          name?: string | null
          org_number?: string | null
          registration_date?: string | null
          remark_control?: string | null
          sni_code?: string | null
          status?: string | null
          updated_at?: string
          website?: string | null
        }
        Update: {
          company_form?: string | null
          company_id?: number
          county_seat?: string | null
          created_at?: string
          email?: string | null
          industry?: string | null
          municipal_seat?: string | null
          name?: string | null
          org_number?: string | null
          registration_date?: string | null
          remark_control?: string | null
          sni_code?: string | null
          status?: string | null
          updated_at?: string
          website?: string | null
        }
        Relationships: []
      }
      company_financials: {
        Row: {
          annual_result: number | null
          cash_liquidity: number | null
          company_id: number
          created_at: string
          employee_count: number | null
          finance_id: number
          fiscal_year: string
          profit_margin: number | null
          report_url: string | null
          result_after_financial_items: number | null
          risk_buffer: number | null
          share_capital: number | null
          solidity: number | null
          total_assets: number | null
          turnover: number | null
        }
        Insert: {
          annual_result?: number | null
          cash_liquidity?: number | null
          company_id: number
          created_at?: string
          employee_count?: number | null
          finance_id?: number
          fiscal_year: string
          profit_margin?: number | null
          report_url?: string | null
          result_after_financial_items?: number | null
          risk_buffer?: number | null
          share_capital?: number | null
          solidity?: number | null
          total_assets?: number | null
          turnover?: number | null
        }
        Update: {
          annual_result?: number | null
          cash_liquidity?: number | null
          company_id?: number
          created_at?: string
          employee_count?: number | null
          finance_id?: number
          fiscal_year?: string
          profit_margin?: number | null
          report_url?: string | null
          result_after_financial_items?: number | null
          risk_buffer?: number | null
          share_capital?: number | null
          solidity?: number | null
          total_assets?: number | null
          turnover?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "company_financials_company_id_fkey"
            columns: ["company_id"]
            isOneToOne: false
            referencedRelation: "companies"
            referencedColumns: ["company_id"]
          },
        ]
      }
      company_roles: {
        Row: {
          company_id: number
          created_at: string
          end_date: string | null
          is_beneficial_owner: boolean | null
          person_id: number
          role_id: number
          role_name: string | null
          start_date: string | null
        }
        Insert: {
          company_id: number
          created_at?: string
          end_date?: string | null
          is_beneficial_owner?: boolean | null
          person_id: number
          role_id?: number
          role_name?: string | null
          start_date?: string | null
        }
        Update: {
          company_id?: number
          created_at?: string
          end_date?: string | null
          is_beneficial_owner?: boolean | null
          person_id?: number
          role_id?: number
          role_name?: string | null
          start_date?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "company_roles_company_id_fkey"
            columns: ["company_id"]
            isOneToOne: false
            referencedRelation: "companies"
            referencedColumns: ["company_id"]
          },
          {
            foreignKeyName: "company_roles_person_id_fkey"
            columns: ["person_id"]
            isOneToOne: false
            referencedRelation: "persons"
            referencedColumns: ["person_id"]
          },
        ]
      }
      contact_messages: {
        Row: {
          created_at: string
          email: string
          id: string
          message: string
          name: string
          subject: string
        }
        Insert: {
          created_at?: string
          email: string
          id?: string
          message: string
          name: string
          subject: string
        }
        Update: {
          created_at?: string
          email?: string
          id?: string
          message?: string
          name?: string
          subject?: string
        }
        Relationships: []
      }
      courses: {
        Row: {
          content: Json | null
          created_at: string
          description: string | null
          difficulty_level: string | null
          estimated_duration: number | null
          id: string
          is_published: boolean | null
          order_index: number | null
          title: string
          updated_at: string
        }
        Insert: {
          content?: Json | null
          created_at?: string
          description?: string | null
          difficulty_level?: string | null
          estimated_duration?: number | null
          id?: string
          is_published?: boolean | null
          order_index?: number | null
          title: string
          updated_at?: string
        }
        Update: {
          content?: Json | null
          created_at?: string
          description?: string | null
          difficulty_level?: string | null
          estimated_duration?: number | null
          id?: string
          is_published?: boolean | null
          order_index?: number | null
          title?: string
          updated_at?: string
        }
        Relationships: []
      }
      credit_transactions: {
        Row: {
          amount: number
          created_at: string
          description: string | null
          id: string
          reference_id: string | null
          transaction_type: string
          user_id: string | null
        }
        Insert: {
          amount: number
          created_at?: string
          description?: string | null
          id?: string
          reference_id?: string | null
          transaction_type: string
          user_id?: string | null
        }
        Update: {
          amount?: number
          created_at?: string
          description?: string | null
          id?: string
          reference_id?: string | null
          transaction_type?: string
          user_id?: string | null
        }
        Relationships: []
      }
      data_quality_metrics: {
        Row: {
          completeness: number | null
          consistency: number | null
          entity_id: number | null
          entity_type: string | null
          field_name: string | null
          measured_at: string
          metric_id: number
          validity: number | null
        }
        Insert: {
          completeness?: number | null
          consistency?: number | null
          entity_id?: number | null
          entity_type?: string | null
          field_name?: string | null
          measured_at?: string
          metric_id?: number
          validity?: number | null
        }
        Update: {
          completeness?: number | null
          consistency?: number | null
          entity_id?: number | null
          entity_type?: string | null
          field_name?: string | null
          measured_at?: string
          metric_id?: number
          validity?: number | null
        }
        Relationships: []
      }
      erasure_tombstones: {
        Row: {
          entity_id: string
          entity_table: string
          erased_at: string | null
          erasure_reason: string | null
          id: string
          requested_by: string | null
        }
        Insert: {
          entity_id: string
          entity_table: string
          erased_at?: string | null
          erasure_reason?: string | null
          id?: string
          requested_by?: string | null
        }
        Update: {
          entity_id?: string
          entity_table?: string
          erased_at?: string | null
          erasure_reason?: string | null
          id?: string
          requested_by?: string | null
        }
        Relationships: []
      }
      export_history: {
        Row: {
          created_at: string
          credits_used: number
          download_url: string | null
          expires_at: string | null
          export_type: string
          file_name: string
          file_size_mb: number | null
          id: string
          status: string
          user_id: string | null
        }
        Insert: {
          created_at?: string
          credits_used?: number
          download_url?: string | null
          expires_at?: string | null
          export_type: string
          file_name: string
          file_size_mb?: number | null
          id?: string
          status?: string
          user_id?: string | null
        }
        Update: {
          created_at?: string
          credits_used?: number
          download_url?: string | null
          expires_at?: string | null
          export_type?: string
          file_name?: string
          file_size_mb?: number | null
          id?: string
          status?: string
          user_id?: string | null
        }
        Relationships: []
      }
      fetches: {
        Row: {
          bytes_downloaded: number | null
          created_at: string
          duration_ms: number | null
          error_message: string | null
          http_status: number | null
          id: string
          page_id: string
          proxy_id: string | null
          started_at: string
        }
        Insert: {
          bytes_downloaded?: number | null
          created_at?: string
          duration_ms?: number | null
          error_message?: string | null
          http_status?: number | null
          id?: string
          page_id: string
          proxy_id?: string | null
          started_at: string
        }
        Update: {
          bytes_downloaded?: number | null
          created_at?: string
          duration_ms?: number | null
          error_message?: string | null
          http_status?: number | null
          id?: string
          page_id?: string
          proxy_id?: string | null
          started_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "fetches_page_id_fkey"
            columns: ["page_id"]
            isOneToOne: false
            referencedRelation: "pages"
            referencedColumns: ["id"]
          },
        ]
      }
      gcs_files: {
        Row: {
          bucket_name: string
          content_type: string | null
          created_at: string
          gcs_updated_at: string | null
          id: string
          md5_hash: string | null
          metadata: Json
          object_name: string
          project_id: string | null
          size: number | null
          synced_at: string
        }
        Insert: {
          bucket_name: string
          content_type?: string | null
          created_at?: string
          gcs_updated_at?: string | null
          id?: string
          md5_hash?: string | null
          metadata?: Json
          object_name: string
          project_id?: string | null
          size?: number | null
          synced_at?: string
        }
        Update: {
          bucket_name?: string
          content_type?: string | null
          created_at?: string
          gcs_updated_at?: string | null
          id?: string
          md5_hash?: string | null
          metadata?: Json
          object_name?: string
          project_id?: string | null
          size?: number | null
          synced_at?: string
        }
        Relationships: []
      }
      idempotency_keys: {
        Row: {
          created_at: string | null
          key: string
          method: string
          path: string
          response_body: Json | null
          response_status: number | null
          tenant_id: string | null
        }
        Insert: {
          created_at?: string | null
          key: string
          method: string
          path: string
          response_body?: Json | null
          response_status?: number | null
          tenant_id?: string | null
        }
        Update: {
          created_at?: string | null
          key?: string
          method?: string
          path?: string
          response_body?: Json | null
          response_status?: number | null
          tenant_id?: string | null
        }
        Relationships: []
      }
      links: {
        Row: {
          anchor_text: string | null
          created_at: string
          destination_url: string
          id: number
          rel_attr: string | null
          source_page_id: string
        }
        Insert: {
          anchor_text?: string | null
          created_at?: string
          destination_url: string
          id?: number
          rel_attr?: string | null
          source_page_id: string
        }
        Update: {
          anchor_text?: string | null
          created_at?: string
          destination_url?: string
          id?: number
          rel_attr?: string | null
          source_page_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "links_source_page_id_fkey"
            columns: ["source_page_id"]
            isOneToOne: false
            referencedRelation: "pages"
            referencedColumns: ["id"]
          },
        ]
      }
      news: {
        Row: {
          author_id: string | null
          content: string | null
          created_at: string
          excerpt: string | null
          featured_image_url: string | null
          id: string
          is_published: boolean | null
          published_at: string | null
          title: string
          updated_at: string
        }
        Insert: {
          author_id?: string | null
          content?: string | null
          created_at?: string
          excerpt?: string | null
          featured_image_url?: string | null
          id?: string
          is_published?: boolean | null
          published_at?: string | null
          title: string
          updated_at?: string
        }
        Update: {
          author_id?: string | null
          content?: string | null
          created_at?: string
          excerpt?: string | null
          featured_image_url?: string | null
          id?: string
          is_published?: boolean | null
          published_at?: string | null
          title?: string
          updated_at?: string
        }
        Relationships: []
      }
      oauth_clients: {
        Row: {
          client_id: string
          client_secret_hash: string
          created_at: string | null
          id: string
          scopes: Json
          tenant_id: string | null
          updated_at: string | null
        }
        Insert: {
          client_id: string
          client_secret_hash: string
          created_at?: string | null
          id?: string
          scopes?: Json
          tenant_id?: string | null
          updated_at?: string | null
        }
        Update: {
          client_id?: string
          client_secret_hash?: string
          created_at?: string | null
          id?: string
          scopes?: Json
          tenant_id?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
      page_views: {
        Row: {
          id: string
          page_path: string
          viewed_at: string
        }
        Insert: {
          id?: string
          page_path: string
          viewed_at?: string
        }
        Update: {
          id?: string
          page_path?: string
          viewed_at?: string
        }
        Relationships: []
      }
      pages: {
        Row: {
          canonical_url: string | null
          created_at: string
          depth: number | null
          etag: string | null
          host: string
          http_status: number | null
          id: string
          last_fetch_at: string | null
          last_modified: string | null
          template_guess: string | null
          url: string
        }
        Insert: {
          canonical_url?: string | null
          created_at?: string
          depth?: number | null
          etag?: string | null
          host: string
          http_status?: number | null
          id?: string
          last_fetch_at?: string | null
          last_modified?: string | null
          template_guess?: string | null
          url: string
        }
        Update: {
          canonical_url?: string | null
          created_at?: string
          depth?: number | null
          etag?: string | null
          host?: string
          http_status?: number | null
          id?: string
          last_fetch_at?: string | null
          last_modified?: string | null
          template_guess?: string | null
          url?: string
        }
        Relationships: []
      }
      person_addresses: {
        Row: {
          address_id: number
          city: string | null
          county: string | null
          created_at: string
          end_date: string | null
          municipality: string | null
          person_id: number
          postal_code: string | null
          special_address: string | null
          start_date: string | null
          street: string | null
        }
        Insert: {
          address_id?: number
          city?: string | null
          county?: string | null
          created_at?: string
          end_date?: string | null
          municipality?: string | null
          person_id: number
          postal_code?: string | null
          special_address?: string | null
          start_date?: string | null
          street?: string | null
        }
        Update: {
          address_id?: number
          city?: string | null
          county?: string | null
          created_at?: string
          end_date?: string | null
          municipality?: string | null
          person_id?: number
          postal_code?: string | null
          special_address?: string | null
          start_date?: string | null
          street?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "person_addresses_person_id_fkey"
            columns: ["person_id"]
            isOneToOne: false
            referencedRelation: "persons"
            referencedColumns: ["person_id"]
          },
        ]
      }
      person_contacts: {
        Row: {
          contact_id: number
          created_at: string
          kind: string | null
          last_porting_date: string | null
          operator: string | null
          person_id: number
          phone_number_enc: string | null
          phone_number_hash: string | null
          previous_operator: string | null
          user_type: string | null
        }
        Insert: {
          contact_id?: number
          created_at?: string
          kind?: string | null
          last_porting_date?: string | null
          operator?: string | null
          person_id: number
          phone_number_enc?: string | null
          phone_number_hash?: string | null
          previous_operator?: string | null
          user_type?: string | null
        }
        Update: {
          contact_id?: number
          created_at?: string
          kind?: string | null
          last_porting_date?: string | null
          operator?: string | null
          person_id?: number
          phone_number_enc?: string | null
          phone_number_hash?: string | null
          previous_operator?: string | null
          user_type?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "person_contacts_person_id_fkey"
            columns: ["person_id"]
            isOneToOne: false
            referencedRelation: "persons"
            referencedColumns: ["person_id"]
          },
        ]
      }
      persons: {
        Row: {
          birth_date: string | null
          civil_status: string | null
          created_at: string
          economy_summary: string | null
          first_name: string | null
          gender: Database["public"]["Enums"]["gender_enum"] | null
          has_remarks: boolean | null
          last_name: string | null
          middle_name: string | null
          person_id: number
          personal_number_enc: string | null
          personal_number_hash: string | null
          salary_decimal: number | null
          updated_at: string
        }
        Insert: {
          birth_date?: string | null
          civil_status?: string | null
          created_at?: string
          economy_summary?: string | null
          first_name?: string | null
          gender?: Database["public"]["Enums"]["gender_enum"] | null
          has_remarks?: boolean | null
          last_name?: string | null
          middle_name?: string | null
          person_id?: number
          personal_number_enc?: string | null
          personal_number_hash?: string | null
          salary_decimal?: number | null
          updated_at?: string
        }
        Update: {
          birth_date?: string | null
          civil_status?: string | null
          created_at?: string
          economy_summary?: string | null
          first_name?: string | null
          gender?: Database["public"]["Enums"]["gender_enum"] | null
          has_remarks?: boolean | null
          last_name?: string | null
          middle_name?: string | null
          person_id?: number
          personal_number_enc?: string | null
          personal_number_hash?: string | null
          salary_decimal?: number | null
          updated_at?: string
        }
        Relationships: []
      }
      profiles: {
        Row: {
          avatar_url: string | null
          bio: string | null
          company: string | null
          created_at: string
          email: string
          full_name: string | null
          id: string
          phone: string | null
          preferences: Json | null
          tenant_id: string | null
          updated_at: string
          user_id: string | null
        }
        Insert: {
          avatar_url?: string | null
          bio?: string | null
          company?: string | null
          created_at?: string
          email: string
          full_name?: string | null
          id?: string
          phone?: string | null
          preferences?: Json | null
          tenant_id?: string | null
          updated_at?: string
          user_id?: string | null
        }
        Update: {
          avatar_url?: string | null
          bio?: string | null
          company?: string | null
          created_at?: string
          email?: string
          full_name?: string | null
          id?: string
          phone?: string | null
          preferences?: Json | null
          tenant_id?: string | null
          updated_at?: string
          user_id?: string | null
        }
        Relationships: []
      }
      projects: {
        Row: {
          active: boolean
          created_at: string
          description: string | null
          id: string
          title: string
          updated_at: string
        }
        Insert: {
          active?: boolean
          created_at?: string
          description?: string | null
          id?: string
          title: string
          updated_at?: string
        }
        Update: {
          active?: boolean
          created_at?: string
          description?: string | null
          id?: string
          title?: string
          updated_at?: string
        }
        Relationships: []
      }
      provenance_records: {
        Row: {
          created_at: string | null
          entity_id: string
          entity_table: string
          id: string
          job_id: string | null
          source_url: string | null
          template_id: string | null
          template_version: number | null
        }
        Insert: {
          created_at?: string | null
          entity_id: string
          entity_table: string
          id?: string
          job_id?: string | null
          source_url?: string | null
          template_id?: string | null
          template_version?: number | null
        }
        Update: {
          created_at?: string | null
          entity_id?: string
          entity_table?: string
          id?: string
          job_id?: string | null
          source_url?: string | null
          template_id?: string | null
          template_version?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "provenance_records_template_id_fkey"
            columns: ["template_id"]
            isOneToOne: false
            referencedRelation: "templates"
            referencedColumns: ["id"]
          },
        ]
      }
      referrals: {
        Row: {
          activated_at: string | null
          created_at: string
          credits_earned: number | null
          id: string
          referred_email: string
          referred_user_id: string | null
          referrer_id: string | null
          status: string
        }
        Insert: {
          activated_at?: string | null
          created_at?: string
          credits_earned?: number | null
          id?: string
          referred_email: string
          referred_user_id?: string | null
          referrer_id?: string | null
          status?: string
        }
        Update: {
          activated_at?: string | null
          created_at?: string
          credits_earned?: number | null
          id?: string
          referred_email?: string
          referred_user_id?: string | null
          referrer_id?: string | null
          status?: string
        }
        Relationships: []
      }
      role_permissions: {
        Row: {
          role_name: string
          scope: string
        }
        Insert: {
          role_name: string
          scope: string
        }
        Update: {
          role_name?: string
          scope?: string
        }
        Relationships: []
      }
      scraping_jobs: {
        Row: {
          domain: string | null
          error_text: string | null
          finished_at: string | null
          job_id: number
          job_type: string | null
          params_json: Json | null
          result_location: string | null
          started_at: string | null
          status: string | null
          template_id: number | null
          tenant_id: string | null
        }
        Insert: {
          domain?: string | null
          error_text?: string | null
          finished_at?: string | null
          job_id?: number
          job_type?: string | null
          params_json?: Json | null
          result_location?: string | null
          started_at?: string | null
          status?: string | null
          template_id?: number | null
          tenant_id?: string | null
        }
        Update: {
          domain?: string | null
          error_text?: string | null
          finished_at?: string | null
          job_id?: number
          job_type?: string | null
          params_json?: Json | null
          result_location?: string | null
          started_at?: string | null
          status?: string | null
          template_id?: number | null
          tenant_id?: string | null
        }
        Relationships: []
      }
      site_settings: {
        Row: {
          created_at: string
          cv_file_url: string | null
          id: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          cv_file_url?: string | null
          id?: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          cv_file_url?: string | null
          id?: string
          updated_at?: string
        }
        Relationships: []
      }
      staging_extracts: {
        Row: {
          domain: string
          fetched_at: string
          fingerprint: string | null
          issues_json: Json | null
          job_id: number | null
          payload_json: Json | null
          snapshot_ref: string | null
          staging_id: number
          status: string | null
          template_key: string | null
          url: string
        }
        Insert: {
          domain: string
          fetched_at: string
          fingerprint?: string | null
          issues_json?: Json | null
          job_id?: number | null
          payload_json?: Json | null
          snapshot_ref?: string | null
          staging_id?: number
          status?: string | null
          template_key?: string | null
          url: string
        }
        Update: {
          domain?: string
          fetched_at?: string
          fingerprint?: string | null
          issues_json?: Json | null
          job_id?: number | null
          payload_json?: Json | null
          snapshot_ref?: string | null
          staging_id?: number
          status?: string | null
          template_key?: string | null
          url?: string
        }
        Relationships: [
          {
            foreignKeyName: "staging_extracts_job_id_fkey"
            columns: ["job_id"]
            isOneToOne: false
            referencedRelation: "scraping_jobs"
            referencedColumns: ["job_id"]
          },
        ]
      }
      subscribers: {
        Row: {
          created_at: string
          email: string
          id: string
          stripe_customer_id: string | null
          subscribed: boolean
          subscription_end: string | null
          subscription_tier: string | null
          updated_at: string
          user_id: string | null
        }
        Insert: {
          created_at?: string
          email: string
          id?: string
          stripe_customer_id?: string | null
          subscribed?: boolean
          subscription_end?: string | null
          subscription_tier?: string | null
          updated_at?: string
          user_id?: string | null
        }
        Update: {
          created_at?: string
          email?: string
          id?: string
          stripe_customer_id?: string | null
          subscribed?: boolean
          subscription_end?: string | null
          subscription_tier?: string | null
          updated_at?: string
          user_id?: string | null
        }
        Relationships: []
      }
      subscription_plans: {
        Row: {
          created_at: string
          credits_per_month: number | null
          description: string | null
          features: Json | null
          id: string
          is_active: boolean | null
          max_team_members: number | null
          name: string
          price_monthly: number | null
          price_yearly: number | null
          updated_at: string
        }
        Insert: {
          created_at?: string
          credits_per_month?: number | null
          description?: string | null
          features?: Json | null
          id?: string
          is_active?: boolean | null
          max_team_members?: number | null
          name: string
          price_monthly?: number | null
          price_yearly?: number | null
          updated_at?: string
        }
        Update: {
          created_at?: string
          credits_per_month?: number | null
          description?: string | null
          features?: Json | null
          id?: string
          is_active?: boolean | null
          max_team_members?: number | null
          name?: string
          price_monthly?: number | null
          price_yearly?: number | null
          updated_at?: string
        }
        Relationships: []
      }
      team_members: {
        Row: {
          id: string
          joined_at: string
          role: string
          team_id: string | null
          user_id: string | null
        }
        Insert: {
          id?: string
          joined_at?: string
          role: string
          team_id?: string | null
          user_id?: string | null
        }
        Update: {
          id?: string
          joined_at?: string
          role?: string
          team_id?: string | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "team_members_team_id_fkey"
            columns: ["team_id"]
            isOneToOne: false
            referencedRelation: "teams"
            referencedColumns: ["id"]
          },
        ]
      }
      teams: {
        Row: {
          created_at: string
          created_by: string | null
          description: string | null
          id: string
          name: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          created_by?: string | null
          description?: string | null
          id?: string
          name: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          created_by?: string | null
          description?: string | null
          id?: string
          name?: string
          updated_at?: string
        }
        Relationships: []
      }
      templates: {
        Row: {
          created_at: string | null
          created_by: string | null
          dsl: Json
          id: string
          name: string
          tenant_id: string | null
          updated_at: string | null
          version: number
        }
        Insert: {
          created_at?: string | null
          created_by?: string | null
          dsl: Json
          id?: string
          name: string
          tenant_id?: string | null
          updated_at?: string | null
          version?: number
        }
        Update: {
          created_at?: string | null
          created_by?: string | null
          dsl?: Json
          id?: string
          name?: string
          tenant_id?: string | null
          updated_at?: string | null
          version?: number
        }
        Relationships: []
      }
      transactions: {
        Row: {
          amount: number
          created_at: string
          currency: string | null
          description: string | null
          id: string
          status: string | null
          stripe_payment_id: string | null
          transaction_type: string
          user_id: string
        }
        Insert: {
          amount: number
          created_at?: string
          currency?: string | null
          description?: string | null
          id?: string
          status?: string | null
          stripe_payment_id?: string | null
          transaction_type: string
          user_id: string
        }
        Update: {
          amount?: number
          created_at?: string
          currency?: string | null
          description?: string | null
          id?: string
          status?: string | null
          stripe_payment_id?: string | null
          transaction_type?: string
          user_id?: string
        }
        Relationships: []
      }
      user_api_keys: {
        Row: {
          api_key_hash: string
          created_at: string
          expires_at: string | null
          id: string
          is_active: boolean | null
          key_name: string
          last_used_at: string | null
          permissions: Json | null
          user_id: string | null
        }
        Insert: {
          api_key_hash: string
          created_at?: string
          expires_at?: string | null
          id?: string
          is_active?: boolean | null
          key_name: string
          last_used_at?: string | null
          permissions?: Json | null
          user_id?: string | null
        }
        Update: {
          api_key_hash?: string
          created_at?: string
          expires_at?: string | null
          id?: string
          is_active?: boolean | null
          key_name?: string
          last_used_at?: string | null
          permissions?: Json | null
          user_id?: string | null
        }
        Relationships: []
      }
      user_course_progress: {
        Row: {
          completed_at: string | null
          completed_modules: Json | null
          course_id: string
          id: string
          last_accessed: string | null
          progress_percentage: number | null
          started_at: string | null
          user_id: string
        }
        Insert: {
          completed_at?: string | null
          completed_modules?: Json | null
          course_id: string
          id?: string
          last_accessed?: string | null
          progress_percentage?: number | null
          started_at?: string | null
          user_id: string
        }
        Update: {
          completed_at?: string | null
          completed_modules?: Json | null
          course_id?: string
          id?: string
          last_accessed?: string | null
          progress_percentage?: number | null
          started_at?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_course_progress_course_id_fkey"
            columns: ["course_id"]
            isOneToOne: false
            referencedRelation: "courses"
            referencedColumns: ["id"]
          },
        ]
      }
      user_credits: {
        Row: {
          balance: number
          id: string
          total_earned: number
          total_spent: number
          updated_at: string
          user_id: string | null
        }
        Insert: {
          balance?: number
          id?: string
          total_earned?: number
          total_spent?: number
          updated_at?: string
          user_id?: string | null
        }
        Update: {
          balance?: number
          id?: string
          total_earned?: number
          total_spent?: number
          updated_at?: string
          user_id?: string | null
        }
        Relationships: []
      }
      user_dashboards: {
        Row: {
          created_at: string
          dashboard_config: Json | null
          description: string | null
          id: string
          is_shared: boolean | null
          name: string
          updated_at: string
          user_id: string | null
        }
        Insert: {
          created_at?: string
          dashboard_config?: Json | null
          description?: string | null
          id?: string
          is_shared?: boolean | null
          name: string
          updated_at?: string
          user_id?: string | null
        }
        Update: {
          created_at?: string
          dashboard_config?: Json | null
          description?: string | null
          id?: string
          is_shared?: boolean | null
          name?: string
          updated_at?: string
          user_id?: string | null
        }
        Relationships: []
      }
      user_datasets: {
        Row: {
          access_level: string | null
          created_at: string
          data_source: string | null
          description: string | null
          id: string
          name: string
          size_mb: number | null
          updated_at: string
          user_id: string | null
        }
        Insert: {
          access_level?: string | null
          created_at?: string
          data_source?: string | null
          description?: string | null
          id?: string
          name: string
          size_mb?: number | null
          updated_at?: string
          user_id?: string | null
        }
        Update: {
          access_level?: string | null
          created_at?: string
          data_source?: string | null
          description?: string | null
          id?: string
          name?: string
          size_mb?: number | null
          updated_at?: string
          user_id?: string | null
        }
        Relationships: []
      }
      user_devices: {
        Row: {
          browser: string | null
          created_at: string
          device_name: string
          device_type: string
          id: string
          is_current_device: boolean | null
          last_login: string | null
          operating_system: string | null
          user_id: string
        }
        Insert: {
          browser?: string | null
          created_at?: string
          device_name: string
          device_type: string
          id?: string
          is_current_device?: boolean | null
          last_login?: string | null
          operating_system?: string | null
          user_id: string
        }
        Update: {
          browser?: string | null
          created_at?: string
          device_name?: string
          device_type?: string
          id?: string
          is_current_device?: boolean | null
          last_login?: string | null
          operating_system?: string | null
          user_id?: string
        }
        Relationships: []
      }
      user_quotas: {
        Row: {
          current_usage: number
          limit: number
          period_end: string | null
          period_start: string | null
          quota_type: string
          tenant_id: string
          updated_at: string | null
        }
        Insert: {
          current_usage?: number
          limit: number
          period_end?: string | null
          period_start?: string | null
          quota_type: string
          tenant_id: string
          updated_at?: string | null
        }
        Update: {
          current_usage?: number
          limit?: number
          period_end?: string | null
          period_start?: string | null
          quota_type?: string
          tenant_id?: string
          updated_at?: string | null
        }
        Relationships: []
      }
      user_roles: {
        Row: {
          created_at: string
          id: string
          role: string
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          role?: string
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          id?: string
          role?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      user_settings: {
        Row: {
          created_at: string
          id: string
          language_preference: string | null
          notification_preferences: Json | null
          privacy_settings: Json | null
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          language_preference?: string | null
          notification_preferences?: Json | null
          privacy_settings?: Json | null
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          id?: string
          language_preference?: string | null
          notification_preferences?: Json | null
          privacy_settings?: Json | null
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      user_subscriptions: {
        Row: {
          created_at: string
          id: string
          stripe_customer_id: string | null
          stripe_subscription_id: string | null
          subscribed: boolean
          subscription_end: string | null
          subscription_start: string | null
          subscription_tier: string
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          stripe_customer_id?: string | null
          stripe_subscription_id?: string | null
          subscribed?: boolean
          subscription_end?: string | null
          subscription_start?: string | null
          subscription_tier?: string
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          id?: string
          stripe_customer_id?: string | null
          stripe_subscription_id?: string | null
          subscribed?: boolean
          subscription_end?: string | null
          subscription_start?: string | null
          subscription_tier?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      vehicle_history: {
        Row: {
          created_at: string
          event_date: string | null
          event_desc: string | null
          event_kind: string | null
          event_link: string | null
          history_id: number
          raw_json: Json | null
          vehicle_id: number
        }
        Insert: {
          created_at?: string
          event_date?: string | null
          event_desc?: string | null
          event_kind?: string | null
          event_link?: string | null
          history_id?: number
          raw_json?: Json | null
          vehicle_id: number
        }
        Update: {
          created_at?: string
          event_date?: string | null
          event_desc?: string | null
          event_kind?: string | null
          event_link?: string | null
          history_id?: number
          raw_json?: Json | null
          vehicle_id?: number
        }
        Relationships: [
          {
            foreignKeyName: "vehicle_history_vehicle_id_fkey"
            columns: ["vehicle_id"]
            isOneToOne: false
            referencedRelation: "vehicles"
            referencedColumns: ["vehicle_id"]
          },
        ]
      }
      vehicle_ownership: {
        Row: {
          company_id: number | null
          created_at: string
          end_date: string | null
          owner_kind: Database["public"]["Enums"]["owner_kind"]
          person_id: number | null
          role: string | null
          start_date: string | null
          vehicle_id: number
          vehicle_owner_id: number
        }
        Insert: {
          company_id?: number | null
          created_at?: string
          end_date?: string | null
          owner_kind: Database["public"]["Enums"]["owner_kind"]
          person_id?: number | null
          role?: string | null
          start_date?: string | null
          vehicle_id: number
          vehicle_owner_id?: number
        }
        Update: {
          company_id?: number | null
          created_at?: string
          end_date?: string | null
          owner_kind?: Database["public"]["Enums"]["owner_kind"]
          person_id?: number | null
          role?: string | null
          start_date?: string | null
          vehicle_id?: number
          vehicle_owner_id?: number
        }
        Relationships: [
          {
            foreignKeyName: "vehicle_ownership_company_id_fkey"
            columns: ["company_id"]
            isOneToOne: false
            referencedRelation: "companies"
            referencedColumns: ["company_id"]
          },
          {
            foreignKeyName: "vehicle_ownership_person_id_fkey"
            columns: ["person_id"]
            isOneToOne: false
            referencedRelation: "persons"
            referencedColumns: ["person_id"]
          },
          {
            foreignKeyName: "vehicle_ownership_vehicle_id_fkey"
            columns: ["vehicle_id"]
            isOneToOne: false
            referencedRelation: "vehicles"
            referencedColumns: ["vehicle_id"]
          },
        ]
      }
      vehicle_registry: {
        Row: {
          brand: string | null
          created_at: string
          id: string
          model: string | null
          reg_plate: string | null
          updated_at: string
          year: number | null
        }
        Insert: {
          brand?: string | null
          created_at?: string
          id?: string
          model?: string | null
          reg_plate?: string | null
          updated_at?: string
          year?: number | null
        }
        Update: {
          brand?: string | null
          created_at?: string
          id?: string
          model?: string | null
          reg_plate?: string | null
          updated_at?: string
          year?: number | null
        }
        Relationships: []
      }
      vehicle_technical_specs: {
        Row: {
          airbag_info: string | null
          body_type: string | null
          color: string | null
          created_at: string
          curb_weight_kg: number | null
          drive_type: string | null
          engine_power_kw: number | null
          engine_volume_cc: number | null
          fuel_type: string | null
          gearbox: string | null
          height_mm: number | null
          length_mm: number | null
          noise_drive_db: number | null
          passenger_count: number | null
          payload_kg: number | null
          rim_front: string | null
          rim_rear: string | null
          spec_id: number
          tire_front: string | null
          tire_rear: string | null
          top_speed_kmh: number | null
          total_weight_kg: number | null
          trailer_braked_kg: number | null
          trailer_total_b_kg: number | null
          trailer_total_b_plus_kg: number | null
          trailer_unbraked_kg: number | null
          vehicle_id: number
          wheelbase_mm: number | null
          width_mm: number | null
          wltp_co2_g_km: number | null
          wltp_consumption_l_100km: number | null
        }
        Insert: {
          airbag_info?: string | null
          body_type?: string | null
          color?: string | null
          created_at?: string
          curb_weight_kg?: number | null
          drive_type?: string | null
          engine_power_kw?: number | null
          engine_volume_cc?: number | null
          fuel_type?: string | null
          gearbox?: string | null
          height_mm?: number | null
          length_mm?: number | null
          noise_drive_db?: number | null
          passenger_count?: number | null
          payload_kg?: number | null
          rim_front?: string | null
          rim_rear?: string | null
          spec_id?: number
          tire_front?: string | null
          tire_rear?: string | null
          top_speed_kmh?: number | null
          total_weight_kg?: number | null
          trailer_braked_kg?: number | null
          trailer_total_b_kg?: number | null
          trailer_total_b_plus_kg?: number | null
          trailer_unbraked_kg?: number | null
          vehicle_id: number
          wheelbase_mm?: number | null
          width_mm?: number | null
          wltp_co2_g_km?: number | null
          wltp_consumption_l_100km?: number | null
        }
        Update: {
          airbag_info?: string | null
          body_type?: string | null
          color?: string | null
          created_at?: string
          curb_weight_kg?: number | null
          drive_type?: string | null
          engine_power_kw?: number | null
          engine_volume_cc?: number | null
          fuel_type?: string | null
          gearbox?: string | null
          height_mm?: number | null
          length_mm?: number | null
          noise_drive_db?: number | null
          passenger_count?: number | null
          payload_kg?: number | null
          rim_front?: string | null
          rim_rear?: string | null
          spec_id?: number
          tire_front?: string | null
          tire_rear?: string | null
          top_speed_kmh?: number | null
          total_weight_kg?: number | null
          trailer_braked_kg?: number | null
          trailer_total_b_kg?: number | null
          trailer_total_b_plus_kg?: number | null
          trailer_unbraked_kg?: number | null
          vehicle_id?: number
          wheelbase_mm?: number | null
          width_mm?: number | null
          wltp_co2_g_km?: number | null
          wltp_consumption_l_100km?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "vehicle_technical_specs_vehicle_id_fkey"
            columns: ["vehicle_id"]
            isOneToOne: true
            referencedRelation: "vehicles"
            referencedColumns: ["vehicle_id"]
          },
        ]
      }
      vehicles: {
        Row: {
          created_at: string
          emission_class: string | null
          eu_category: string | null
          first_registration_date: string | null
          import_status: string | null
          is_financed: boolean | null
          is_leased: boolean | null
          make: string | null
          model: string | null
          model_year: number | null
          next_inspection: string | null
          owner_count: number | null
          registration_number: string | null
          stolen_status: string | null
          tax_month: number | null
          tax_year1_3: number | null
          tax_year4: number | null
          traffic_in_sweden_since: string | null
          traffic_status: string | null
          type_approval_number: string | null
          updated_at: string
          vehicle_id: number
          vin: string | null
        }
        Insert: {
          created_at?: string
          emission_class?: string | null
          eu_category?: string | null
          first_registration_date?: string | null
          import_status?: string | null
          is_financed?: boolean | null
          is_leased?: boolean | null
          make?: string | null
          model?: string | null
          model_year?: number | null
          next_inspection?: string | null
          owner_count?: number | null
          registration_number?: string | null
          stolen_status?: string | null
          tax_month?: number | null
          tax_year1_3?: number | null
          tax_year4?: number | null
          traffic_in_sweden_since?: string | null
          traffic_status?: string | null
          type_approval_number?: string | null
          updated_at?: string
          vehicle_id?: number
          vin?: string | null
        }
        Update: {
          created_at?: string
          emission_class?: string | null
          eu_category?: string | null
          first_registration_date?: string | null
          import_status?: string | null
          is_financed?: boolean | null
          is_leased?: boolean | null
          make?: string | null
          model?: string | null
          model_year?: number | null
          next_inspection?: string | null
          owner_count?: number | null
          registration_number?: string | null
          stolen_status?: string | null
          tax_month?: number | null
          tax_year1_3?: number | null
          tax_year4?: number | null
          traffic_in_sweden_since?: string | null
          traffic_status?: string | null
          type_approval_number?: string | null
          updated_at?: string
          vehicle_id?: number
          vin?: string | null
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      gender_enum: "unknown" | "female" | "male" | "other"
      owner_kind: "person" | "company"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      gender_enum: ["unknown", "female", "male", "other"],
      owner_kind: ["person", "company"],
    },
  },
} as const
